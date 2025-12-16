from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from app.models.user import User
from app.models.subscription_plan import SubscriptionPlan

class UserRepo:

    @staticmethod
    def change_subscription(db: Session, user: User, new_plan_id: int, stripe_subscription_id: str | None = None):
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == new_plan_id).first()
        if not plan:
            raise ValueError("Plan not found")
        user.subscription_id = plan.id
        # Reset credits according to plan type
        if plan.id == 1:  # Free plan
            user.credits_left = plan.daily_credits
        else:
            user.credits_left = plan.monthly_credits

        user.last_reset = datetime.utcnow()
        if stripe_subscription_id:
            user.stripe_subscription_id = stripe_subscription_id
            user.subscription_status = "active"
        db.commit()
        return user

    @staticmethod
    def deduct_credit(db: Session, user: User):
        if not user.plan:
            raise HTTPException("User has no subscription")
        
        now = datetime.utcnow()
        if user.subscription_id == 1:
            if now - user.last_reset >= timedelta(days=1):
                user.credits_left = user.plan.daily_credits
                user.last_reset = now
                db.commit()
                
        elif user.subscription_id in (2,3):
            if user.last_reset + relativedelta(months=1)<=now:
                user.credits_left = user.plan.monthly_credits
                user.last_reset = now
                db.commit()

        if user.credits_left <= 0:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Daily credits exhausted")

        user.credits_left -= 1
        db.commit()

    @staticmethod 
    def get_credits(db:Session, user:User):
        now = datetime.utcnow()
        if user.subscription_id==1:
            if (now - user.last_reset) >= timedelta(days=1):
                user.credits_left = user.plan.daily_credits
                user.last_reset = now
                db.commit()

        elif user.subscription_id in (2, 3):  # Pro/Enterprise
            if not user.last_reset or user.last_reset + relativedelta(months=1) <= now:
                user.credits_left = user.plan.monthly_credits
                user.last_reset = now
                db.commit()


        return user


