from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    content: str

# Response schema
class MessageResponse(BaseModel):
    id: int
    chat_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True