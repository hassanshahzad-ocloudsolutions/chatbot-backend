from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="New Chat")  # optional title
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, ForeignKey("users.uid"))
    is_archive=Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="chats")
    link = relationship("ChatLinks", back_populates="chat", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="chats", cascade="all, delete-orphan")

