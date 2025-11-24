
from sqlalchemy.orm import Session
from app.models.message import Message

# handle queries (DB operations)

class MessageRepository:

    @staticmethod
    def save_message(db: Session,chat_id,role,content,file_name):
        msg = Message(chat_id=chat_id, role=role, content=content, file_name=file_name)
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg
    

    @staticmethod
    def fetch_by_chat(db: Session, chat_id: int):
        return (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.created_at)
            .all()
        )

    

        

