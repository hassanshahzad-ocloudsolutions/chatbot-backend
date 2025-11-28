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
    is_archive: bool


class RenameChatRequest(BaseModel):
    new_title: str



    class Config:
        orm_mode = True
