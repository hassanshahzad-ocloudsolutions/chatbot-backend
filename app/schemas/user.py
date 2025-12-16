from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# Base schema shared across create/response
class UserBase(BaseModel):
    email: EmailStr
    subscription_status: str

# Used when creating a user
class UserCreate(UserBase):
    uid: str

# Response schema (what API returns)
class UserResponse(UserBase):
    uid: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserRemainingCredits(BaseModel):
    uid:str
    credits_left:int

    class Config:
        orm_mode = True
    
