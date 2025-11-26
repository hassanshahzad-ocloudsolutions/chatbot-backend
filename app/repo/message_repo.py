
from sqlalchemy.orm import Session
from app.models.message import Message

# handle queries (DB operations)

class MessageRepository:

    @staticmethod
    def save_message(db: Session,chat_id,role,content,file_name,audio_content):
        msg = Message(chat_id=chat_id, role=role, content=content, file_name=file_name,audio_content=audio_content)
        db.add(msg)
        db.commit()
        db.refresh(msg)
        print(msg.content, msg.id)
        return msg
    

    @staticmethod
    def fetch_by_chat(db: Session, chat_id: int):
        return (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.created_at)
            .all()
        )
    
    @staticmethod
    def get_latest_message(db:Session, chat_id:int):
       return (db.query(Message)
                    .filter(Message.chat_id == chat_id, Message.role == "user")
                    .order_by(Message.created_at.desc())
                    .first())
    


    

        

