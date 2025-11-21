from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.subscription_serivce import SubscriptionService 
from app.services.user_service import UserService
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/subscription", tags=["subscription"])

@router.get("/plans")
def get_plans(db: Session = Depends(get_db)):
    return SubscriptionService.get_plans(db)

@router.post("/subscribe/{plan_id}")
def subscribe_plan(plan_id: int, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    success_url = "https://google.com" #in case payment is succesfull route to google.com
    cancel_url = "https://facebook.com" #in case payment is cancelled route to facebook.com
    try:
        return SubscriptionService.subscribe_user(db, user, plan_id, success_url, cancel_url)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))