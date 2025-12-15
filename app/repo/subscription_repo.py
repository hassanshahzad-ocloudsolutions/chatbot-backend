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
        
        return db.query(SubscriptionPlan).all()

    @staticmethod
    def create_stripe_checkout(db: Session, user: User, plan_id: int, success_url: str, cancel_url: str):
        """
        - If user has no stripe subscription -> create Checkout Session (new subscription).
        - If user has stripe_subscription_id:
            - If new plan price > current plan price -> upgrade immediately (modify subscription)
            - If new plan price < current plan price -> schedule downgrade via metadata (pending_plan_id) and no immediate change
            - If equal price -> immediate switch (modify subscription)
        """
        new_plan = SubscriptionRepo.get_plan(db, plan_id)
        if not new_plan:
            raise HTTPException(status_code=404, detail="Plan not found")

        # Free plan -> assign immediately
        if new_plan.price_cents == 0:
            user.subscription_id = new_plan.id
            user.credits_left = new_plan.daily_credits
            user.last_reset = datetime.utcnow()
            db.commit()
            return {"message": f"Subscribed to {new_plan.name} (free plan)"}


        if user.stripe_subscription_id:
            # Load current local plan
            current_plan = SubscriptionRepo.get_plan(db, user.subscription_id)
            print(current_plan.id)

            # Retrieve stripe subscription to access items and metadata
            try:
                stripe_sub = stripe.Subscription.retrieve(user.stripe_subscription_id)
                print("Inside try of user.stripe_subscription_id ")
                print(stripe_sub)
            except stripe.error.StripeError as e:
                raise HTTPException(status_code=502, detail=f"Failed to retrieve Stripe subscription: {e}")

            # Safeguard: ensure there is at least one subscription item
            items = stripe_sub.get("items", {}).get("data", [])
            print(items)
            if not items:
                raise HTTPException(status_code=400, detail="Stripe subscription has no items")

            subscription_item_id = items[0]["id"]
            print(subscription_item_id)

            # Upgrade: immediate (new price > current)
            if new_plan.price_cents > (current_plan.price_cents or 0):
                try:
                    print("In Upgrade")
                    stripe.Subscription.modify(
                        user.stripe_subscription_id,
                        cancel_at_period_end=False,
                        items=[{
                            "id": subscription_item_id,
                            "price": new_plan.stripe_price_id
                        }],
                        proration_behavior="none",
                        billing_cycle_anchor="now",
                        metadata={"pending_plan_id": "",
                                  "uid":str(user.uid),
                                  "plan_id": str(new_plan.id)}
                    )
                    print(f"Upgrade initiated in Stripe to plan {new_plan.id}")
                    items = stripe_sub.get("items", {}).get("data", [])
                    subscription_item_id = items[0]["id"]
                    print(subscription_item_id)

                except stripe.error.StripeError as e:
                    raise HTTPException(status_code=502, detail=f"Stripe error while upgrading: {e}")
                return {
                "message": f"Upgrade to {new_plan.name} initiated. You'll be charged the  amount.",
                "note": "Your plan will be updated once payment is confirmed."}
            
               # Downgrade: delayed -> use metadata pending_plan_id (no immediate DB change)
            elif new_plan.price_cents < (current_plan.price_cents or 0):
                try:
                    print("In downgrade")
                    current_subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
                    subscription_item_id = current_subscription["items"]["data"][0]["id"]
                    stripe.Subscription.modify(
                        user.stripe_subscription_id,
                        cancel_at_period_end=False,
                        items=[{
                        "id": subscription_item_id,
                        "price": new_plan.stripe_price_id}],
                        proration_behavior="none",  # No immediate charge or credit
                        billing_cycle_anchor="unchanged",  # Keep current billing date (Jan 20)
                        metadata={
                            "old_plan_id": str(current_plan.id),
                            "plan_id": str(new_plan.id),
                            "uid": str(user.uid),
                            "pending_downgrade": "true"})
                    
                    print(f"Downgrade scheduled: Next payment will be ${new_plan.price_cents/100}")
                    
                except stripe.error.StripeError as e:
                    raise HTTPException(status_code=502, detail=f"Stripe error while scheduling downgrade: {e}")

                return {"message": f"Downgrade to {new_plan.name} scheduled for next billing cycle"}

            # Same price: immediate swap
            else:
                try:

                    stripe.Subscription.modify(
                        user.stripe_subscription_id,
                        cancel_at_period_end=False,
                        items=[{
                            "id": subscription_item_id,
                            "price": new_plan.stripe_price_id
                        }],
                        proration_behavior="none",
                        metadata={"pending_plan_id": "",
                                  "uid": str(user.uid),
                                  "plan_id": str(new_plan.id) }  # clear pending downgrades if any
                    )
                except stripe.error.StripeError as e:
                    raise HTTPException(status_code=502, detail=f"Stripe error while switching plan: {e}")

                return {
                "message": f"Switch to {new_plan.name} initiated.",
                "note": "Your plan will be updated shortly."
            }


            
        # No existing stripe subscription -> create a Checkout Session to start a new subscription
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{"price": new_plan.stripe_price_id, "quantity": 1}],
                success_url=success_url,
                cancel_url=cancel_url,
                subscription_data={
                    "metadata": {
                        "user_id": str(user.uid),
                        "plan_id": str(new_plan.id)
                    }
                }
            )
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=502, detail=f"Stripe Checkout creation failed: {e}")

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
    
    @staticmethod
    def get_current_subscription(db:Session, user:User):
        subscription = (db.query(SubscriptionPlan.name)
        .join(User, User.subscription_id == SubscriptionPlan.id)
        .filter(User.uid == user.uid)
        .first())

        return subscription


