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
        event = stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook")

      # Handle events
    if event.type == "invoice.payment_succeeded":
        invoice = event.data.object
        # Get subscription ID
        
        lines = invoice.get("lines", {}).get("data", [])
        first_line = lines[0] if len(lines) > 0 else {}

        stripe_subscription_id = (
        first_line.get("parent", {})
        .get("subscription_item_details", {})
        .get("subscription"))
    
        # Get metadata
        metadata = first_line.get("metadata", {})
        uid = metadata.get("user_id", None)
        plan_id= metadata.get("plan_id", None)
  
        if not uid or not plan_id:
            return {"status": "ignored - missing metadata"}

        # Find user by uid
        user = db.query(User).filter(User.uid == uid).first()
        if not user:
            return {"status": "user_not_found"}
        
        try:
            UserService.change_subscription_service(
                    db=db,
                    user=user,
                    new_plan_id=int(plan_id), 
                    stripe_subscription_id=stripe_subscription_id
                )
              # Clear metadata after successful update
            stripe.Subscription.modify(
            stripe_subscription_id,
            metadata={**metadata,"plan_id": ""})
            return {"status": "success"}
        
        except Exception as e:
            return {"status": "error", "detail": str(e)} 

    elif event.type=="customer.subscription.deleted":
        invoice = event.data.object
        stripe_subscription_id = invoice.get("id")

        if not stripe_subscription_id:
            raise ValueError("Stripe subscription ID is missing in event.data.object")
        
        user = db.query(User).filter(User.stripe_subscription_id == stripe_subscription_id).first()
        if user:    
            SubscriptionService.cancel_user_subscription_and_set_free_plan_service(db, user)
            return {"status": "success", "event": "customer.subscription.deleted"}
        return {"status": "ignored", "reason": "User not found"}
    
    elif event.type == "invoice.payment_failed":
        invoice = event.data.object

        lines = invoice.get("lines", {}).get("data", [])
        first_line = lines[0] if len(lines) > 0 else {}

        stripe_subscription_id = (
        first_line.get("parent", {})
        .get("subscription_item_details", {})
        .get("subscription", None))

        metadata = first_line.get("metadata", {})
        uid = metadata.get("user_id")

        # Find user by stripe_subscription_id
        user = db.query(User).filter(User.stripe_subscription_id == stripe_subscription_id).first()
        if user:    
            SubscriptionService.cancel_user_subscription_and_set_free_plan_service(db, user)
            return {"status": "success", "event": "Payment failed so cancelled the subscription"}
        return {"status": "ignored", "reason": "User not found"}
    
    else:
        return {"status": "ignored"}
    
    


        
