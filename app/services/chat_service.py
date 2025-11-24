from sqlalchemy import desc
from app.services.chatbot_service import Ollama, OpenAi, LangChain
from sqlalchemy.orm import Session
from app.models.chat import Chat
from app.models.message import Message
from typing import List
from app.repo.chat_repo import ChatRepository
from app.repo.message_repo import MessageRepository


#routes business logics
def create_chat_service(db: Session, user_id: int)->Chat:
    return ChatRepository.create_chat(db, user_id)

def get_chat_by_id_service(db:Session, chat_id:int, user_id)->Chat:
    chat = ChatRepository.get_chat_by_id(db, chat_id, user_id)
    if not chat:
        raise ValueError("Chat not found")
    return chat

def save_message_service(db:Session,chat_id,role,content,file_name)->Message:
    msg = MessageRepository.save_message(db, chat_id, role, content,file_name)
    if not msg:
        raise ValueError("Message not found")
    return msg
    
#The logic is mostly business logic: “generate a title for a chat using AI” so keep it here
def generate_title_service(db: Session, chat: Chat, user_message: str )->str:
    ai_response = bot_title_service(f"Generate a short title: {user_message}")
    chat.title = ai_response
    db.commit()
    db.refresh(chat)
    return chat.title

def bot_response_service(db, chat_id, prompt, file):
    return LangChain().generate_response(db,chat_id,prompt,file)

def bot_title_service(prompt):
    return LangChain().generate_title(prompt)

def fetch_messages_by_chat_service(db:Session, chat_id)->List[Message]:
    messages = MessageRepository.fetch_by_chat(db,chat_id)
    return messages

def fetch_chat_history_service(db:Session, user_id)->List[Chat]:
    chats = ChatRepository.get_all_chats(db, user_id)
    return chats

def delete_chat_service(db: Session,chat_id, user_id)->None:
    chat = ChatRepository.get_chat_by_id(db, chat_id, user_id)
    if not chat:
        raise ValueError("Chat not found")
    ChatRepository.delete_chat(db, chat)
    
