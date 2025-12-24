
from fastapi import HTTPException, logger
from sqlalchemy.orm import Session
import stripe
from app.models.user import User
from app.repo.subscription_repo import SubscriptionRepo
from app.schemas.subscription import SubscriptionResponse
from app.stripe.subscription_actions import SubscriptionActions

class SubscriptionService:

    @staticmethod
    def get_plans_service(db: Session):
        return SubscriptionRepo.get_all_plans(db)

    @staticmethod
    def subscribe_user_service(db: Session, user: User, plan_id: int, success_url: str, cancel_url: str):
        new_plan = SubscriptionRepo.get_plan(db, plan_id)
        current_plan = SubscriptionRepo.get_plan(db, user.subscription_id)

        if not new_plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        if new_plan.price_cents == 0:
            SubscriptionRepo.assign_free_plan(db, user, new_plan)
            return SubscriptionResponse(
                status="updated",
                message=f"Subscribed to {new_plan.name} (free)"
            )
        
        if not user.stripe_subscription_id:
            try:
                checkout = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    mode="subscription",
                    line_items=[{"price": new_plan.stripe_price_id, "quantity": 1}],
                    success_url=success_url,
                    cancel_url=cancel_url,
                    customer_email=user.email,
                    subscription_data={
                        "metadata": {
                            "user_id": str(user.uid),
                            "plan_id": str(new_plan.id)
                        }
                    }
                )
                return {
                "status": "checkout_required",
                "checkout_url": checkout.url
            }

            except stripe.error.StripeError as e:
                logger.error("StripeError occurred", exc_info=True)
                # Extract useful details
                err_type = type(e).__name__
                err_msg = str(e)
                status_code = getattr(e, "http_status", "N/A")
                stripe_code = getattr(e, "code", "N/A")
                request_id = getattr(e, "request_id", "N/A")
            
                raise HTTPException(
                    status_code=502,
                    detail={
                        "error_type": err_type,
                        "message": err_msg,
                        "http_status": status_code,
                        "stripe_code": stripe_code,
                        "request_id": request_id
                    }
                )


        #In case user is already on some subscription
        stripe_sub = stripe.Subscription.retrieve(user.stripe_subscription_id)
        items = stripe_sub.get("items", {}).get("data", [])
        subscription_item_id = items[0]["id"]

        # Upgrade: immediate (new price > current)
        if new_plan.id > current_plan.id:
            SubscriptionActions.upgrade_subscription(
                new_plan.id,
                user.stripe_subscription_id,
                subscription_item_id,
                new_plan.stripe_price_id,
                stripe_sub #for metadata
            )
            return {
                "status": "pending_payment",
                "message": "Upgrade initiated. Enterprise plan will apply after payment succeeds."
            }
        
        if new_plan.id < current_plan.id:
            SubscriptionActions.downgrade(
                user,
                db,
                new_plan.id,
                user.stripe_subscription_id,
                new_plan.stripe_price_id,
                stripe_sub #for metadata
            )
            return {
                "status": "scheduled",
                "message": "Downgrade scheduled for next billing cycle."
            }
        
        #for same plan prop->pro, enterprise->enterprise but no payment deduction
        if new_plan.id == current_plan.id:
            SubscriptionActions.switch_same_plan(
                user,
                db,
                new_plan.id,
                user.stripe_subscription_id,
                subscription_item_id,
                new_plan.stripe_price_id,
                stripe_sub
            )
            return {
            "status": "pending_payment_same_plan",
            "message": "Subscription reactivated without any charge as you were on this plan before. Payment will be charged in next billing cycle."
            }

    @staticmethod
    def set_cancel_user_subscription_service(db:Session, user:User):
        if not user.stripe_subscription_id:
            raise ValueError("User has no active Stripe subscription")
        subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
        schedule_id = subscription.get('schedule')
        # If a schedule exists, release it so we can modify the subscription directly
        if schedule_id:
            stripe.SubscriptionSchedule.release(schedule_id)

        try:
            stripe.Subscription.modify(
                user.stripe_subscription_id,
                cancel_at_period_end=True
            )

        except Exception as e:  # fallback for any Stripe error
            raise ValueError(f"Stripe error: {e}")
        
        user.subscription_status = "cancel"
        db.commit()
        return user
    
    @staticmethod
    def cancel_user_subscription_and_set_free_plan_service(db:Session, user: User):
        return SubscriptionRepo.cancel_to_free(db,user)
    
    @staticmethod
    def get_current_subscription_serivce(db:Session, user:User):
        return SubscriptionRepo.get_current_subscription(db,user)
    
