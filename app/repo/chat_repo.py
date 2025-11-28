
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, select
from app.models.chat import Chat
from app.models.chat_links import ChatLinks
from app.models.message import Message

# handle queries (DB operations)

class ChatRepository:

    @staticmethod
    def create_chat(db: Session, user_id):
        chat = Chat(user_id=user_id, title="New Chat")
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat
    
    @staticmethod
    def get_chat_by_id(db: Session, chat_id: int, user_id):
        return (
            db.query(Chat)
            .filter(Chat.id == chat_id, Chat.user_id == user_id)
            .first()
        )
    
    @staticmethod
    def get_all_chats(db: Session, user_id):
        return db.query(Chat).filter(Chat.user_id==user_id, Chat.is_archive==False).order_by(desc(Chat.created_at)).all()
    
    @staticmethod
    def delete_chat(db:Session, chat:Chat):
        db.delete(chat)
        db.commit()

    @staticmethod
    def save_link(db:Session, chat_id,read_only):

        link = ChatLinks(
            chat_id=chat_id,
            read_only=read_only,
            created_at=datetime.utcnow()
        )
        db.add(link)
        db.commit()
        db.refresh(link)
        return link

    @staticmethod
    def get_link_token(db:Session, chat_id):
        stmt = select(ChatLinks.id).where(ChatLinks.chat_id == chat_id).limit(1)
        result = db.execute(stmt).scalar()  # returns the first ID or None if no row
        return result

    @staticmethod
    def get_chat_link_uuid(db:Session,token):
        return db.query(ChatLinks).filter(ChatLinks.id == token).first()

    @staticmethod
    def check_chat_exists_by_link_uuid(db:Session, link_chat_id):
        return db.query(Chat).filter(Chat.id == link_chat_id).first()

    @staticmethod
    def search_chats(db:Session,user_id: str,query: Optional[str] = None) ->List[Chat]:
        """
        Search chats by title or any message content for a given user
        """
        if not query:
            return []

        # Join Chat with Message to search in both title and messages
        return (
            db.query(Chat)
            .join(Message, Message.chat_id == Chat.id)
            .filter(
                Chat.user_id == user_id,
                or_(
                    Chat.title.ilike(f"%{query}%"),
                    Message.content.ilike(f"%{query}%")
                )
            )
            .distinct()
            .order_by(Chat.created_at.desc())
            .all()
        )
    
    @staticmethod
    def archive_the_chat(db:Session, chat_id,user_id)->Chat:
        chat = (
            db.query(Chat)
            .filter(Chat.id == chat_id, Chat.user_id == user_id)
            .first()
        )
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        chat.is_archive = True
        db.commit()
        db.refresh(chat)
        return chat
    
    @staticmethod
    def unarchive_the_chat(db:Session, chat_id, user_id)->Chat:
        chat = (
            db.query(Chat)
            .filter(Chat.id == chat_id, Chat.user_id == user_id)
            .first()
        )
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        chat.is_archive = False
        db.commit()
        db.refresh(chat)
        return chat
    
    @staticmethod
    def fetch_all_archive_chats(db:Session, user_id)->List[Chat]:
        chats = db.query(Chat).filter(Chat.user_id==user_id, Chat.is_archive==True).order_by(desc(Chat.created_at)).all()
        return chats
    
    @staticmethod
    def delete_all_archive_chats(db:Session, user_id)->int:
        archived_chats = db.query(Chat).filter(Chat.user_id==user_id,Chat.is_archive==True)
        count = archived_chats.count()
        if count == 0:
            return 0

        # Delete all in a single query
        archived_chats.delete(synchronize_session=False)
        db.commit()
        return count
    
    @staticmethod
    def delete_all_chats(db:Session, user_id)->int:
        user_chats = db.query(Chat).filter(Chat.user_id == user_id)

        count = user_chats.count()
        if count == 0:
            return 0

        # Bulk delete
        user_chats.delete(synchronize_session=False)
        db.commit()
        return count




    
