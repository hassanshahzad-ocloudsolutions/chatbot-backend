from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from sqlalchemy.orm import relationship

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)          # Free, Pro, Enterprise
    daily_credits = Column(Integer)
    price_cents = Column(Integer, default=0)    # 0 for free plan
    stripe_price_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="plan")

