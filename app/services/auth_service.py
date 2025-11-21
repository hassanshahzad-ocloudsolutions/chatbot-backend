from fastapi import HTTPException, Depends, Header
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.firebase_service import verify_firebase_token
from datetime import datetime
from app.repo.subscription_repo import SubscriptionRepo
from app.models.subscription_plan import SubscriptionPlan

#not need to include or register in routes as it is not our an endpoint but will be used by other end points

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):

    """
    Get user from Firebase token in Authorization header
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token header")

    firebase_token = authorization.split(" ")[1]

    decoded_token = verify_firebase_token(firebase_token)
    uid = decoded_token.get("uid")
    email = decoded_token.get("email")

    if not uid or not email:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

    user = db.query(User).filter(User.uid == uid).first()

    # Get Free plan
    if not user:
        # Ensure Free plan exists
        free_plan = db.query(SubscriptionPlan).filter_by(name="Free").first()
        # Create new user with Free plan
        user = User(
            uid=uid,
            email=email,
            subscription_id=free_plan.id,
            credits_left=free_plan.daily_credits,
            last_reset=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user





