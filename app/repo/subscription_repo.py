from sqlalchemy.orm import Session
from app.models.subscription_plan import SubscriptionPlan
from app.models.user import User
import stripe
from app.config import STRIPE_API_KEY
from datetime import datetime
from fastapi import HTTPException

stripe.api_key = STRIPE_API_KEY

class SubscriptionRepo:
   
    @staticmethod
    def get_plan(db: Session, plan_id: int):
        return db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()

    @staticmethod
    def get_all_plans(db: Session):
        return db.query(SubscriptionPlan).order_by(SubscriptionPlan.id).all()


    @staticmethod
    def cancel_to_free(db: Session, user: User):
        # Cancel Stripe subscription if exists
        # Get Free plan
        free_plan = db.query(SubscriptionPlan).filter_by(name="Free").first()
        if not free_plan:
            raise ValueError("Free plan not found")

        # Downgrade user to Free plan
        user.subscription_id = free_plan.id
        user.credits_left = free_plan.daily_credits
        user.last_reset = datetime.utcnow()
        user.stripe_subscription_id = None
        user.subscription_status = "deleted"

        db.commit()
        return user
    
    @staticmethod
    def get_current_subscription(db:Session, user:User):
        subscription = (db.query(SubscriptionPlan.name)
        .join(User, User.subscription_id == SubscriptionPlan.id)
        .filter(User.uid == user.uid)
        .first())

        return subscription
    
    @staticmethod
    def assign_free_plan(db:Session, user: User,plan):
        user.subscription_id = plan.id
        user.credits_left = plan.daily_credits
        user.last_reset = datetime.utcnow()
        user.subscription_status = "inactive"
        db.commit()

