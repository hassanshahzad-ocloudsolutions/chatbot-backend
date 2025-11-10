from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from sqlalchemy.orm import Session
from models.user import User
from services.firebase_service import verify_firebase_token


route_auth = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

def get_current_user(firebase_token: str, db: Session = Depends(get_db)):
    """
    Accepts Firebase ID token, verifies it, creates user if not exists,
    and returns user info.
    """
    # Verify token
    decoded_token = verify_firebase_token(firebase_token)
    uid = decoded_token.get("uid")
    email = decoded_token.get("email")

    if not uid or not email:
        raise HTTPException(status_code=400, detail="Invalid Firebase token")

    # Check if user exists in DB
    user = db.query(User).filter(User.uid == uid).first()
    if not user:
        # Create new user
        user = User(uid=uid, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user




