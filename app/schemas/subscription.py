from pydantic import BaseModel
from typing import Optional

class CurrentSubscriptionSchema(BaseModel):
    subscription_id: Optional[int]
    subscription_name: Optional[str]  # added from join
    credits_left: int
    stripe_subscription_id: Optional[str]

    class Config:
        orm_mode = True

#after subscription is done
class SubscriptionResponse(BaseModel):
    status: str  
    message: str
    checkout_url: Optional[str] = None
