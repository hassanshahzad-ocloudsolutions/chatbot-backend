from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from schemas.message import MessageResponse  # import for nested output

class ChatBase(BaseModel):
    title: Optional[str] = "New Chat"

class ChatCreate(ChatBase):
    user_id: str

class ChatResponse(ChatBase):
    id: int
    created_at: datetime
    user_id: str
    messages: List[MessageResponse] = []  # include messages in chat response

    class Config:
        orm_mode = True
