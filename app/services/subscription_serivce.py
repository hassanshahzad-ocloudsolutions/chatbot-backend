
from sqlalchemy.orm import Session
from app.models.user import User
from app.repo.subscription_repo import SubscriptionRepo

class SubscriptionService:

    @staticmethod
    def get_plans_service(db: Session):
        return SubscriptionRepo.get_all_plans(db)

    @staticmethod
    def subscribe_user_service(db: Session, user: User, plan_id: int, success_url: str, cancel_url: str):
        return SubscriptionRepo.create_stripe_checkout(db, user, plan_id, success_url, cancel_url)
    
    @staticmethod
    def set_cancel_user_subscription_service(db:Session, user:User):
        return SubscriptionRepo.set_cancellation(db, user)
    
    @staticmethod
    def cancel_user_subscription_and_set_free_plan_service(db:Session, user: User):
        return SubscriptionRepo.cancel_to_free(db,user)
    
  
