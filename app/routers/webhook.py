from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.repo.user_repo import UserRepo
from app.repo.subscription_repo import SubscriptionRepo
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

        print(event.data)
        invoice = event.data.object
        stripe_subscription_id = invoice.get("subscription")
        metadata = invoice.get("metadata", {})
        uid = metadata.get("user_id")

        # Find user by stripe_subscription_id
        user = db.query(User).filter(User.uid == uid).first()
        if user:
            # Use your change_subscription function to reset credits
            UserRepo.change_subscription(
                db=db,
                user=user,
                new_plan_id=user.subscription_id,  # keep the same plan
                stripe_subscription_id=stripe_subscription_id
            )


    return {"status": "success"}
