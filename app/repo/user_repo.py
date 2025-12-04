from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.user import User
from app.models.subscription_plan import SubscriptionPlan

class UserRepo:

    @staticmethod
    def change_subscription(db: Session, user: User, new_plan_id: int, stripe_subscription_id: str | None = None):
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == new_plan_id).first()
        if not plan:
            raise ValueError("Plan not found")
        user.subscription_id = plan.id
        user.credits_left = plan.daily_credits
        user.last_reset = datetime.utcnow()
        if stripe_subscription_id:
            user.stripe_subscription_id = stripe_subscription_id
        db.commit()
        return user

    @staticmethod
    def deduct_credit(db: Session, user: User):
        if not user.plan:
            raise HTTPException("User has no subscription")

        if datetime.utcnow() - user.last_reset >= timedelta(days=1):
            user.credits_left = user.plan.daily_credits
            user.last_reset = datetime.utcnow()
            db.commit()
            print(datetime.utcnow)

        if user.credits_left <= 0:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Daily credits exhausted")

        user.credits_left -= 1
        db.commit()

