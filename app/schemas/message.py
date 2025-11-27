from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageCreate(BaseModel):
    content: str

# Response schema
class MessageResponse(BaseModel):
    id: int
    role: str
    content: str|None
    created_at: datetime
    file_name: Optional[str]

    class Config:
        orm_mode = True