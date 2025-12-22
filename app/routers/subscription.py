from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.subscription_plan import SubscriptionPlan
from app.services.subscription_serivce import SubscriptionService 
from app.services.user_service import UserService
from app.services.auth_service import get_current_user
from app.models.user import User
from app.config import STRIPE_SUCCESS_URL,STRIPE_FAILURE_URL

router = APIRouter(prefix="/subscription", tags=["subscription"])

@router.get("/plans")
def get_plans(db: Session = Depends(get_db)):
    return SubscriptionService.get_plans_service(db)

@router.post("/subscribe/{plan_id}")
def subscribe_plan(plan_id: int, db: Session = Depends(get_db),user: User = Depends(get_current_user)):
    success_url = STRIPE_SUCCESS_URL 
    cancel_url = STRIPE_FAILURE_URL 
    try:
        return SubscriptionService.subscribe_user_service(db, user, plan_id, success_url, cancel_url)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.post("/cancel")
def cancel_subscription(db: Session = Depends(get_db),
                        user: User = Depends(get_current_user)):
    if not user.subscription_id or not user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription to cancel")
    SubscriptionService.set_cancel_user_subscription_service(db, user)
    return {"message": "Subscription cancelled. You will be downgraded to Free plan with 10 daily credits after the billing month ends."}

@router.get("/current")
def get_current_subscription(db:Session= Depends(get_db), user:User = Depends(get_current_user)):
     # Join User with SubscriptionPlan to get subscription_name
    subscription = SubscriptionService.get_current_subscription_serivce(db, user)

    subscription_name = subscription[0] if subscription else None

    return {
        "subscription_id": user.subscription_id,
        "subscription_name": subscription_name, 
        "credits_left": user.credits_left,
        "last_reset": user.last_reset,
        "stripe_subscription_id": user.stripe_subscription_id,
        "subscription_status":user.subscription_status
    }
