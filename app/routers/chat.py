
from typing import List
from app.database import get_db
from fastapi import APIRouter,Depends, HTTPException
from app.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.schemas.chat import ChatResponse
from app.schemas.message import MessageResponse
from app.services.auth_service import get_current_user
from app.services.chat_service import (create_chat_service,get_chat_by_id_service,
                                       save_message_service, generate_title_service,
                                       bot_response_service, fetch_messages_by_chat_service,
                                       fetch_chat_history_service, delete_chat_service)
from app.services.user_service import UserService
from fastapi import Form, File, UploadFile

router = APIRouter(
    prefix="/chats",
    tags=["chat"]
)

#the left side panel, start new chart button
@router.post("/start")
async def start_chat(db: Session = Depends(get_db),  user: User = Depends(get_current_user)):
    chat = create_chat_service(db, user_id=user.uid )
    return {"message": "Chat started", "chat_id": chat.id}

#sending message and geting response of specific chat, the central panel of my Neural Chat
@router.post("/{chat_id}/messages")
async def send_message(
    chat_id: int,
    message: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Verify chat belongs to user
    try: 
        chat = get_chat_by_id_service(db, chat_id=chat_id, user_id=user.uid)
    except ValueError:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    try:
        UserService.deduct_credit_service(db, user)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    file_name = file.filename if file else None
    # Store user message
    save_message_service(db, chat_id, "user", content=message or "", file_name=file_name,audio_content=None)

    if chat.title == "New Chat" and message:
        try:
            generate_title_service(db, chat, message)
        except Exception as e:
            raise e 

    # Generate AI response from Open AI
    bot_response = bot_response_service(db,chat_id,message,file)

    # Store bot message
    save_message_service(db,chat_id=chat_id, role="assistant", content=bot_response, file_name=None, audio_content=None)

    return {"response": bot_response}


#central panel, loads all messages of specific selected chat
@router.get("/{chat_id}/history", response_model=List[MessageResponse])
async def get_messages(chat_id:int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    chat = get_chat_by_id_service(db, chat_id=chat_id, user_id=user.uid)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    messages = fetch_messages_by_chat_service(db, chat_id)
    return messages

#left panel displaying the chat history of user
@router.get("/", response_model=List[ChatResponse])
async def charts_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    chats = fetch_chat_history_service(db, user_id=user.uid)
    return chats

#deleting a chat
@router.delete("/delete/{chat_id}")
async def delete_chat(chat_id:int, db: Session = Depends(get_db), user: User= Depends(get_current_user)):
    delete_chat_service(db, chat_id, user_id=user.uid)
    return {"message": f"Chat {chat_id} deleted successfully"}