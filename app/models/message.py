from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    role = Column(String)  # "user" or "assistant"
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    chats = relationship("Chat", back_populates="messages")
