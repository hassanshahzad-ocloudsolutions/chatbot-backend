
from typing import List
from app.database import get_db
from fastapi import APIRouter,Depends, HTTPException
from app.models.chat import Chat
from app.models.user import User
from app.models.message import Message
from app.services.chatbot_service import Ollama
from sqlalchemy.orm import Session
from app.schemas.message import MessageCreate
from sqlalchemy import desc
from app.schemas.chat import ChatResponse
from app.schemas.message import MessageResponse
from app.services.auth_service import get_current_user


router = APIRouter(
    prefix="/chats",
    tags=["chat"]
)

def ollama_response(content):
    return Ollama().generate_response(content)

#the left side panel, start new chart button
@router.post("/start")
async def start_chat(db: Session = Depends(get_db),  user: User = Depends(get_current_user)):

    chat = Chat(user_id=user.uid, title="New Chat")
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return {"message": "Chat started", "chat_id": chat.id}

#sending message and geting response of specific chat, the central panel of my Neural Chat
@router.post("/{chat_id}/messages")
async def send_message(
    chat_id: int,
    request: MessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Verify chat belongs to user
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.uid).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Store user message
    user_msg = Message(chat_id=chat_id, role="user", content=request.content)
    db.add(user_msg)
    db.commit()

    # Generate AI response from Ollama
    bot_response = ollama_response(request.content)

    # Store bot message
    bot_msg = Message(chat_id=chat_id, role="assistant", content=bot_response)
    db.add(bot_msg)
    db.commit()

    return {"response": bot_response}


#central panel, loads all messages of specific selected chat
@router.get("/{chat_id}/history", response_model=List[MessageResponse])
async def get_messages(chat_id:int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.uid).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
    return messages

#left panel displaying the chat history of user
@router.get("/", response_model=List[ChatResponse])
async def charts_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    chats = db.query(Chat).filter(Chat.user_id==user.uid).order_by(desc(Chat.created_at)).all()
    return chats

#deleting a chat
@router.delete("/delete/{chat_id}")
async def delete_chat(chat_id:int, db: Session = Depends(get_db), user: User= Depends(get_current_user)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.uid).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.delete(chat)
    db.commit()
    
    return {"message": f"Chat {chat_id} deleted successfully"}