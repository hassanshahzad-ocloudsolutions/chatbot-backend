from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatBase(BaseModel):
    title: Optional[str] = "New Chat"

class ChatCreate(ChatBase):
    user_id: str

class ChatResponse(ChatBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
