from sqlalchemy.orm import Session
from app.models.user import User
from app.repo.user_repo import UserRepo

class UserService:

    @staticmethod
    def deduct_credit_service(db: Session, user: User):
        return UserRepo.deduct_credit(db, user)

    @staticmethod
    def change_subscription_service(db: Session, user: User, new_plan_id: int, stripe_subscription_id: str | None = None):
        return UserRepo.change_subscription(db, user, new_plan_id, stripe_subscription_id)
    
