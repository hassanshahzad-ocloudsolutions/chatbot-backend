

from fastapi import HTTPException
import stripe
from app.models.user import User
from sqlalchemy.orm import Session


class SubscriptionActions:

    @staticmethod
    def upgrade_subscription(new_plan_id,stripe_subscription_id, subscription_item_id, stripe_price_id, stripe_sub):
        try:
            subscription = stripe.Subscription.retrieve(stripe_subscription_id)
            schedule_id = subscription.get('schedule')
        # If a schedule exists, release it so we can modify the subscription directly
            if schedule_id:
                stripe.SubscriptionSchedule.release(schedule_id)

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
    def downgrade(user:User,db:Session,new_plan_id,stripe_subscription_id,stripe_price_id, stripe_sub):
        try:
            items = stripe_sub.get("items", {}).get("data", [])
            current_period_end = items[0]["current_period_end"]
            current_period_start = items[0]["current_period_start"]
            current_price_id = items[0]['price']['id']

            existing_schedules = stripe.SubscriptionSchedule.list(limit=100)
            schedule = next((s for s in existing_schedules.data if s.subscription == stripe_subscription_id), None)

            schedule_id = schedule.id if schedule else stripe.SubscriptionSchedule.create(
                from_subscription=stripe_subscription_id
            ).id

            stripe.SubscriptionSchedule.modify(
            schedule_id,
            phases=[
                {
                    "items": [{"price": current_price_id, "quantity": 1}],
                    "start_date": current_period_start,
                    "end_date": current_period_end
                },
                {
                    "items": [{"price": stripe_price_id, "quantity": 1}],
                    "start_date": current_period_end
                }
            ],
            end_behavior="release", 
            metadata={
                **stripe_sub.metadata,
                "plan_id": str(new_plan_id),
                "current_plan_id": str(user.subscription_id)
            } )
            
            #For webhook
            stripe.Subscription.modify(
            stripe_subscription_id,
            metadata={
                **stripe_sub.metadata,
                "plan_id": str(new_plan_id),
                "user_id": str(user.uid)
            }
        )

        except stripe.error.StripeError as e:
            raise HTTPException(status_code=502, detail=f"Stripe error while scheduling downgrade: {e}")

        user.subscription_status = "active"
        db.commit()
                       
      
    @staticmethod
    def switch_same_plan(user:User,db:Session, new_plan_id, stripe_subscription_id, subscription_item_id, stripe_price_id, stripe_sub):
        try:
            subscription = stripe.Subscription.retrieve(stripe_subscription_id)
            schedule_id = subscription.get('schedule')
        # If a schedule exists, release it so we can modify the subscription directly
            if schedule_id:
                stripe.SubscriptionSchedule.release(schedule_id)

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