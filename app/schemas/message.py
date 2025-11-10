from pydantic import BaseModel
from datetime import datetime

class MessageBase(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class MessageCreate(MessageBase):
    chat_id: int

class MessageResponse(MessageBase):
    id: int
    chat_id: int
    created_at: datetime

    class Config:
        orm_mode = True
