import json
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
        print(json.dumps(event, separators=(',', ':')))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

      # Handle events
    if event.type == "invoice.payment_succeeded":
        invoice = event.data.object
        # Get subscription ID
        stripe_subscription_id = invoice["lines"]["data"][0]["parent"]["subscription_item_details"]["subscription"]
        # Get metadata
        metadata = invoice["lines"]["data"][0]["metadata"]
        uid = metadata.get("user_id")
        plan_id= metadata.get("plan_id")
    
        if not uid or not plan_id:
            return {"status": "ignored - missing metadata"}

        # Find user by uid
        user = db.query(User).filter(User.uid == uid).first()
        if user:
            try:
                # Use your change_subscription function to reset credits
                UserService.change_subscription_service(
                    db=db,
                    user=user,
                    new_plan_id=int(plan_id), 
                    stripe_subscription_id=stripe_subscription_id
                )
            except Exception as e:
                # Log or handle error; don't fail webhook entirely
                return {"details":"Error applying checkout subscription to DB"}

        # Clear metadata after successful update
        stripe.Subscription.modify(
            stripe_subscription_id,
            metadata={**metadata,"plan_id": ""}
        )
        return {"status": "success"}

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
    
    


        
