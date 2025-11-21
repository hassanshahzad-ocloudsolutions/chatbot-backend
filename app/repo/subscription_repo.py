from sqlalchemy.orm import Session
from app.models.subscription_plan import SubscriptionPlan
from app.models.user import User
import stripe
from app.config import STRIPE_API_KEY
from datetime import datetime

stripe.api_key = STRIPE_API_KEY

class SubscriptionRepo:
   

    @staticmethod
    def get_plan(db: Session, plan_id: int):
        return db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()

    @staticmethod
    def get_all_plans(db: Session):
        
        return db.query(SubscriptionPlan).all()

    @staticmethod
    def create_stripe_checkout(db: Session, user: User, plan_id: int, success_url: str, cancel_url: str):
        plan = SubscriptionRepo.get_plan(db, plan_id)
        if not plan:
            raise ValueError("Plan not found")
        
        #creates product and get stripe_price_id that will be stored inside subscription_plans table
        if not plan.stripe_price_id and plan.price_cents > 0:
            product = stripe.Product.create(name=plan.name)
            price = stripe.Price.create(
                product=product.id,
                unit_amount=plan.price_cents,
                currency="usd",
                recurring={"interval": "month"}
            )
            plan.stripe_price_id = price.id
            db.commit()

        if plan.price_cents == 0:
            # Free plan: assign directly
            user.subscription_id = plan.id
            user.credits_left = plan.daily_credits
            user.last_reset = datetime.utcnow()
            db.commit()
            return {"message": "Subscribed to free plan"}

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": plan.stripe_price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            subscription_data={
                "metadata": {
                    "user_id": user.uid,
                    "plan_id": plan.id
                }
            }
        )
        return {"checkout_url": checkout_session.url}
