from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CurrentSubscriptionSchema(BaseModel):
    subscription_id: Optional[int]
    subscription_name: Optional[str]  # added from join
    credits_left: int
    stripe_subscription_id: Optional[str]

    class Config:
        orm_mode = True