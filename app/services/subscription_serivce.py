
from sqlalchemy.orm import Session
from app.models.user import User
from app.repo.subscription_repo import SubscriptionRepo

class SubscriptionService:

    @staticmethod
    def get_plans(db: Session):
        return SubscriptionRepo.get_all_plans(db)

    @staticmethod
    def subscribe_user(db: Session, user: User, plan_id: int, success_url: str, cancel_url: str):
        return SubscriptionRepo.create_stripe_checkout(db, user, plan_id, success_url, cancel_url)
