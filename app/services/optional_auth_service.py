from typing import Optional
from fastapi import Header, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.database import get_db
from app.services.auth_service import get_current_user  # import your existing function
from app.models.user import User

def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Returns the logged-in user if Authorization header is present,
    otherwise returns None for anonymous access.
    """
    if not authorization:
        return None  

    try:
        user = get_current_user(authorization=authorization, db=db)
        return user
    except HTTPException:
        # If auth fails, treat as anonymous
        return None
