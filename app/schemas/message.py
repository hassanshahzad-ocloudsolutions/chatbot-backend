from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=300)

# Response schema
class MessageResponse(BaseModel):
    id: int
    role: str
    content: str|None
    created_at: datetime
    file_name: Optional[str]

    class Config:
        orm_mode = True