from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.schemas.user import UserRemainingCredits
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["user"])

@router.get("/credits", response_model=UserRemainingCredits)
def get_remaining_credits(db:Session=Depends(get_db) ,user:User = Depends(get_current_user)):
    try:
        return UserService.get_credits_service(db, user)  # returning only the uid and credits_left of the filtered user
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")
    

