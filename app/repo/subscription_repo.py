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
                    "user_id": str(user.uid),
                    "plan_id": str(plan.id)
                }
            }
        )
        return {"checkout_url": checkout_session.url}
    
    @staticmethod
    def set_cancellation(db: Session, user: User):
        # Cancel Stripe subscription if exists
        """
        Set the Stripe subscription to cancel at the end of the current billing period.
        User keeps their credits until the subscription actually ends.
        """
        if not user.stripe_subscription_id:
            raise ValueError("User has no active Stripe subscription")

        try:
            stripe.Subscription.modify(
                user.stripe_subscription_id,
                cancel_at_period_end=True
            )
        except Exception as e:  # fallback for any Stripe error
            raise ValueError(f"Stripe error: {e}")

        # Keep subscription_id and credits as is until webhook triggers actual cancellation
        return user
    
    @staticmethod
    def cancel_to_free(db: Session, user: User):
        # Cancel Stripe subscription if exists
        if user.stripe_subscription_id:
            try:
                stripe.Subscription.delete(user.stripe_subscription_id)
            except Exception as e:  # fallback for any Stripe error
                raise ValueError(f"Stripe error: {e}")

        # Get Free plan
        free_plan = db.query(SubscriptionPlan).filter_by(name="Free").first()
        if not free_plan:
            raise ValueError("Free plan not found")

        # Downgrade user to Free plan
        user.subscription_id = free_plan.id
        user.credits_left = free_plan.daily_credits
        user.last_reset = datetime.utcnow()
        user.stripe_subscription_id = None

        db.commit()
        return user


