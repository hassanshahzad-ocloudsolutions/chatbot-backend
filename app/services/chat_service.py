from fastapi import HTTPException
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
        raise HTTPException(status_code=404, detail="Chat not found") 
    return chat

def save_message_service(db:Session,chat_id,role,content,file_name,audio_content)->Message:
    msg = MessageRepository.save_message(db, chat_id, role, content,file_name,audio_content)
    if not msg:
        raise HTTPException(status_code=404, detail="Message could not be saved")
    return msg
    
#The logic is mostly business logic: “generate a title for a chat using AI” so keep it here
def generate_title_service(db: Session, chat: Chat, user_message: str )->str:
    ai_response = bot_title_service(f"Generate a short title: {user_message}")
    if not ai_response:
        raise HTTPException(status_code=500, detail="AI failed to generate a title")
    chat.title = ai_response
    db.commit()
    db.refresh(chat)
    return chat.title

def bot_response_service(db, chat_id, prompt, file):
    response = OpenAi().generate_response(db,chat_id,prompt,file)
    if response is None:
        raise HTTPException(status_code=500, detail="AI response failed")
    return response

def bot_title_service(prompt):
    title = OpenAi().generate_title(prompt)
    if not title:
        raise HTTPException(status_code=500, detail="AI title generation failed")
    return title

def fetch_messages_by_chat_service(db:Session, chat_id)->List[Message]:
    messages = MessageRepository.fetch_by_chat(db,chat_id)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found for this chat")
    return messages

def fetch_chat_history_service(db:Session, user_id)->List[Chat]:
    chats = ChatRepository.get_all_chats(db, user_id)
    if not chats:
        raise HTTPException(status_code=404, detail="No chats found for this user")
    return chats

def delete_chat_service(db: Session,chat_id, user_id)->None:
    chat = ChatRepository.get_chat_by_id(db, chat_id, user_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    ChatRepository.delete_chat(db, chat)


def get_latest_message_service(db:Session, chat_id:int):
    latest_msg = MessageRepository.get_latest_message(db,chat_id)
    if not latest_msg:
        raise HTTPException(status_code=404, detail="No messages found for this chat")
    return latest_msg
    
def  save_link_token_service(db:Session, chat_id, read_only):
    link = ChatRepository.save_link(db,chat_id,read_only)
    if not link:
        raise HTTPException(status_code=500, detail="Failed to save link token")
    return link

def get_link_token_service(db:Session, chat_id):
    token = ChatRepository.get_link_token(db,chat_id)
    return token

def get_chat_link_uuid_service(db:Session, token):
    uuid = ChatRepository.get_chat_link_uuid(db,token)
    if not uuid:
        raise HTTPException(status_code=404, detail="Chat link not found")
    return uuid


def check_chat_exists_by_link_chat_id_service(db:Session, link_chat_id)->bool:
    exists = ChatRepository.check_chat_exists_by_link_uuid(db, link_chat_id)
    if exists is None:
        raise HTTPException(status_code=404, detail="Chat not found by link")
    return exists

def search_chats_service(db: Session,user_id,query)->List[Chat]:
    searched_chats=  ChatRepository.search_chats(db,user_id=user_id, query=query)
    return searched_chats


def archive_the_chat_service(db:Session, chat_id, user_id)->Chat:
    archived_chat = ChatRepository.archive_the_chat(db,chat_id, user_id)
    return archived_chat

def  unarchive_the_chat_service(db:Session, chat_id, user_id)->Chat:
    unarchived_chat = ChatRepository.unarchive_the_chat(db,chat_id,user_id)
    return unarchived_chat

def fetch_all_archive_chats_service(db:Session, user_id)->List[Chat]:
    all_archive = ChatRepository.fetch_all_archive_chats(db, user_id)
    if not all_archive:
        raise HTTPException(status_code=404, detail="No archive chats found for this user")
    return all_archive

def delete_all_archive_chats_service(db:Session, user_id):
    delete_archive_chats_count = ChatRepository.delete_all_archive_chats(db,user_id)
    return delete_archive_chats_count

def  delete_all_chats_service(db:Session, user_id):
    deleted_chats_count = ChatRepository.delete_all_chats(db,user_id)
    return deleted_chats_count