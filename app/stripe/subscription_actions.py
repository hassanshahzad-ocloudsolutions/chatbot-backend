

from fastapi import HTTPException
import stripe
from app.models.user import User
from sqlalchemy.orm import Session


class SubscriptionActions:

    @staticmethod
    def upgrade_subscription(new_plan_id,stripe_subscription_id, subscription_item_id, stripe_price_id, stripe_sub):
        try:
            stripe.Subscription.modify(
                stripe_subscription_id,
                cancel_at_period_end=False,
                items=[{
                    "id": subscription_item_id,
                    "price": stripe_price_id
                    }],
                proration_behavior="none",
                billing_cycle_anchor="now",
                metadata={**stripe_sub.metadata,
                "plan_id": str(new_plan_id)})
    
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=502, detail=f"Stripe error while upgrading: {e}")
        
    @staticmethod
    def downgrade(user:User,db:Session,new_plan_id,stripe_subscription_id, subscription_item_id, stripe_price_id, stripe_sub):
            try:
                stripe.Subscription.modify(
                    stripe_subscription_id,
                    cancel_at_period_end=False,
                    items=[{
                        "id": subscription_item_id,
                        "price": stripe_price_id
                        }],
                        proration_behavior="none",  # No immediate charge or credit
                        billing_cycle_anchor="unchanged",  # Keep current billing date (Jan 20)
                        metadata={**stripe_sub.metadata, "plan_id": str(new_plan_id)}) 
                           
            except stripe.error.StripeError as e:
                raise HTTPException(status_code=502, detail=f"Stripe error while scheduling downgrade: {e}")

            #because it is immediate update
            user.subscription_status="active"
            db.commit()
    
    @staticmethod
    def switch_same_plan(user:User,db:Session, new_plan_id, stripe_subscription_id, subscription_item_id, stripe_price_id, stripe_sub):
        try:
            stripe.Subscription.modify(
                stripe_subscription_id,
                cancel_at_period_end=False,
                items=[{
                    "id": subscription_item_id,
                    "price": stripe_price_id
                       }],
                proration_behavior="none",
                metadata={**stripe_sub.metadata,"plan_id": str(new_plan_id)})
            
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=502, detail=f"Stripe error while switching plan: {e}")

        user.subscription_status="active"
        db.commit()