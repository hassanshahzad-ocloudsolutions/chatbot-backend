from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid



class ChatLinks(Base):
    __tablename__ = "chat_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id"),nullable=False)
    read_only = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship back to Chat
    chat = relationship("Chat", back_populates="link")

