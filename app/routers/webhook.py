from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.repo.subscription_repo import SubscriptionRepo
from app.services.user_service import UserService
from app.services.subscription_serivce import SubscriptionService
from app.models.user import User
from app.config import STRIPE_API_KEY, WEBHOOK_SECRET
import stripe
from datetime import datetime

stripe.api_key = STRIPE_API_KEY

router = APIRouter(prefix="/webhook", tags=["webhook"])

@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # Verify the webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

      # Handle events

    if event.type == "invoice.payment_succeeded":
        invoice = event.data.object
        # Get subscription ID
        stripe_subscription_id = invoice["lines"]["data"][0]["parent"]["subscription_item_details"]["subscription"]
        stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)
        pending_downgrade = stripe_sub.get("metadata", {}).get("pending_downgrade")
        new_plan_id = stripe_sub.get("metadata", {}).get("new_plan_id")

        # Get metadata
        metadata = invoice["lines"]["data"][0]["metadata"]
        uid = metadata.get("user_id")
        plan_id= metadata.get("plan_id")
        pending_plan_id = metadata.get("pending_plan_id")
        pending_price_id = metadata.get("pending_price_id")

        user = None

        # Find user by uid
        user = db.query(User).filter(User.uid == uid).first()
        if user:
            try:
                # Use your change_subscription function to reset credits
                UserService.change_subscription_service(
                    db=db,
                    user=user,
                    new_plan_id=plan_id, 
                    stripe_subscription_id=stripe_subscription_id
                )
            except Exception as e:
                # Log or handle error; don't fail webhook entirely
                print("Error applying checkout subscription to DB:", e)

            if pending_downgrade == "true" and new_plan_id:
                try:
                    print(f"Processing pending downgrade to plan {pending_plan_id}")
                    stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)
                    subscription_item_id = stripe_sub["items"]["data"][0]["id"]
                    # Update Stripe subscription item to pending_price_id

                    new_plan = SubscriptionRepo.get_plan(db, int(new_plan_id))
        
                    if new_plan:
                        user.subscription_id = new_plan.id
                        user.credits_left = new_plan.daily_credits
                        user.last_reset = datetime.utcnow()
                        
                        # Clear the pending downgrade metadata
                        stripe.Subscription.modify(
                            stripe_subscription_id,
                            metadata={
                                "pending_downgrade": "",
                                "old_plan_id": "",
                                "new_plan_id": ""
                            }
                        )
                        
                        db.commit()
                except Exception as e:
                    print("Error applying pending downgrade:", e)

            
        return {"status": "success", "event": "invoice.payment_succeeded"}

   

    elif event.type=="customer.subscription.deleted":
        # Get subscription ID
        stripe_subscription_id =  event.data.object["id"]
        user = db.query(User).filter(User.stripe_subscription_id == stripe_subscription_id).first()
        if user:    
            SubscriptionService.cancel_user_subscription_and_set_free_plan_service(db, user)
            return {"status": "success", "event": "customer.subscription.deleted"}
        return {"status": "ignored", "reason": "User not found"}
    
    elif event.type == "invoice.payment_failed":
        invoice = event.data.object
        metadata = invoice["lines"]["data"][0]["metadata"]
        uid = metadata.get("user_id")
        stripe_subscription_id = invoice["lines"]["data"][0]["parent"]["subscription_item_details"]["subscription"]
        # Find user by stripe_subscription_id
        user = db.query(User).filter(User.stripe_subscription_id == stripe_subscription_id).first()
        if user:    
            SubscriptionService.cancel_user_subscription_and_set_free_plan_service(db, user)
            return {"status": "success", "event": "Payment failed so cancelled the subscription"}
        return {"status": "ignored", "reason": "User not found"}

        

    elif event.type=="customer.subscription.deleted":
        # Get subscription ID
        stripe_subscription_id =  event.data.object["id"]
        user = db.query(User).filter(User.stripe_subscription_id == stripe_subscription_id).first()
        if user:    
            SubscriptionService.cancel_user_subscription_and_set_free_plan_service(db, user)
            return {"status": "success", "event": "customer.subscription.deleted"}
        return {"status": "ignored", "reason": "User not found"}
    
    elif event.type == "invoice.payment_failed":
        invoice = event.data.object
        metadata = invoice["lines"]["data"][0]["metadata"]
        uid = metadata.get("user_id")
        stripe_subscription_id = invoice["lines"]["data"][0]["parent"]["subscription_item_details"]["subscription"]
        # Find user by stripe_subscription_id
        user = db.query(User).filter(User.stripe_subscription_id == stripe_subscription_id).first()
        if user:    
            SubscriptionService.cancel_user_subscription_and_set_free_plan_service(db, user)
            return {"status": "success", "event": "Payment failed so cancelled the subscription"}
        return {"status": "ignored", "reason": "User not found"}
    


        
