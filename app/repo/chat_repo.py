
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.chat import Chat

# handle queries (DB operations)

class ChatRepository:

    @staticmethod
    def create_chat(db: Session, user_id: int):
        chat = Chat(user_id=user_id, title="New Chat")
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat
    
    @staticmethod
    def get_chat_by_id(db: Session, chat_id: int, user_id: int):
        return (
            db.query(Chat)
            .filter(Chat.id == chat_id, Chat.user_id == user_id)
            .first()
        )
    
    @staticmethod
    def get_all_chats(db: Session, user_id):
        return db.query(Chat).filter(Chat.user_id==user_id).order_by(desc(Chat.created_at)).all()
    
    @staticmethod
    def delete_chat(db:Session, chat:Chat):
        db.delete(chat)
        db.commit()

    
