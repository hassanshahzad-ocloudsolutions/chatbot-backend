from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    uid = Column(String, primary_key=True, index=True)  # Firebase UID
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    subscription_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=True ,default=1)
    credits_left = Column(Integer, default=5)
    last_reset = Column(DateTime, default=datetime.utcnow)
    stripe_subscription_id = Column(String, nullable=True)

    chats = relationship("Chat", back_populates="user")
    plan = relationship("SubscriptionPlan", back_populates="users")
