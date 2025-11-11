from database import get_db
from fastapi import APIRouter,Depends, HTTPException
from models.chat import Chat
from models.user import User
from models.message import Message
from services.chatbot_service import Ollama
from routers.auth import get_current_user
from sqlalchemy.orm import Session
from schemas.message import MessageCreate, MessageResponse


router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

#the left side panel start new chart button
@router.post("/start")
def start_chat(
    db: Session = Depends(get_db),  user: User = Depends(get_current_user)):
    chat = Chat(user_id=user.uid, title="New Chat")
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return {"message": "Chat started", "chat_id": chat.id}

#sending message and geting response of specific chat, the central panel of my Neural Chat
@router.post("/{chat_id}/messages" )
def send_message(
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
    bot_response = Ollama().generate_response(request.content)

    # Store bot message
    bot_msg = Message(chat_id=chat_id, role="assistant", content=bot_response)
    db.add(bot_msg)
    db.commit()

    return {"response": bot_response}

