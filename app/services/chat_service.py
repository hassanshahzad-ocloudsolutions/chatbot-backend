from sqlalchemy import desc
from app.services.chatbot_service import Ollama, OpenAi
from sqlalchemy.orm import Session
from app.models.chat import Chat
from app.models.message import Message
from typing import List


def ollama_response(content):
    return Ollama().generate_response(content)

def open_ai_response(content):
    return OpenAi().generate_response(content)

#routes business logics
def create_chat_service(db: Session, user_id: int):
    chat = Chat(user_id=user_id, title="New Chat")
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def get_chat_by_id_service(db:Session, chat_id:int, user_id)->Chat:
    return db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()

def save_message_service(db:Session,chat_id,role,content)->Message:
    msg = Message(chat_id=chat_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def generate_title_service(db: Session, chat: Chat, user_message: str )->str:
    ai_response = OpenAi().generate_response(f"Generate a short title: {user_message}")
    chat.title = ai_response
    db.commit()
    db.refresh(chat)
    return chat.title

def bot_response_service(prompt):
    return OpenAi().generate_response(prompt)

def fetch_messages_service(db:Session, chat_id)->List[Message]:
    return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()

def fetch_chat_history_service(db:Session, user_id)->List[Chat]:
    return db.query(Chat).filter(Chat.user_id==user_id).order_by(desc(Chat.created_at)).all()

def delete_chat_service(db: Session,chat_id, user_id):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise ValueError("Chat not found")
    db.delete(chat)
    db.commit()
