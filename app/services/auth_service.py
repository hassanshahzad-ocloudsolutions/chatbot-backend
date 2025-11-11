from fastapi import HTTPException, Depends, Header
from database import get_db
from sqlalchemy.orm import Session
from models.user import User
from services.firebase_service import verify_firebase_token

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
    if not user:
        user = User(uid=uid, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user





