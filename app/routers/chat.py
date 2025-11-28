
from typing import List, Optional
from app.database import get_db
from fastapi import APIRouter,Depends, HTTPException, Query
from app.models.chat import Chat
from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.chat import ChatResponse
from app.schemas.message import MessageResponse
from app.services.auth_service import get_current_user
from app.services.optional_auth_service import get_optional_user
from app.services.user_service import UserService
from fastapi import Form, File, UploadFile
from uuid import UUID
from app.services.chat_service import (create_chat_service,get_chat_by_id_service,
                                       save_message_service, generate_title_service,
                                       bot_response_service, fetch_messages_by_chat_service,
                                       fetch_chat_history_service, delete_chat_service,
                                       save_link_token_service, get_link_token_service, get_chat_link_uuid_service,
                                       check_chat_exists_by_link_chat_id_service, search_chats_service,
                                       archive_the_chat_service,unarchive_the_chat_service,
                                       fetch_all_archive_chats_service,delete_all_archive_chats_service,
                                       delete_all_chats_service)


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

#deleting an active chat
@router.delete("/delete/{chat_id}")
async def delete_chat(chat_id:int, db: Session = Depends(get_db), user: User= Depends(get_current_user)):
    delete_chat_service(db, chat_id, user_id=user.uid)
    return {"message": f"Chat {chat_id} deleted successfully"}

#generating shareable link of a specifc chat
@router.get("/share/{chat_id}")
async def create_shareable_link(chat_id:int, db:Session = Depends(get_db), user:User =Depends(get_current_user)):
    try: 
        chat = get_chat_by_id_service(db, chat_id=chat_id, user_id=user.uid)
    except ValueError:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    #if already shareable link exists
    uuid_token = get_link_token_service(db, chat_id)
    if uuid_token:
        share_url = f"https://yourapp.com/chat/view/{uuid_token}"
        return {"share_url": share_url}

    #if first time user clicks share button
    save_link_token_service(db,chat_id,read_only=True)
    
    uuid_token = get_link_token_service(db, chat_id)
    share_url = f"https://yourapp.com/chat/view/{uuid_token}" #write here the frontend route like in chatgpt then this route will call below mentioned backend route pasing uuid as path parameter
    return {"share_url": share_url}

#when shareable link put in browser this route will be called and show chat messages
@router.get("/view/{token}")
async def view_chat(token:UUID, db: Session = Depends(get_db), user = Depends(get_optional_user)):
    link = get_chat_link_uuid_service(db,token)
    if not link:
        raise HTTPException(status_code=404, detail="Link invalid")

    chat = check_chat_exists_by_link_chat_id_service(db,link.chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
 
    read_only = link.read_only
    if user and user.uid == chat.user_id:
        # If the logged-in user is the owner, allow full access
        read_only = False

    return {
        "chat_id": chat.id,
        "messages": chat.messages,
        "read_only": read_only
    }


#Search icon in left panel below "new chat icon" to search chat on title and content basis
@router.get("/search",response_model=List[ChatResponse])
def search_chats(query: Optional[str] = Query(None, description="Search query for chat title or message content"),
                db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return search_chats_service(db=db, user_id=current_user.uid, query=query)

#route to archive a specific chat
@router.put("/{chat_id}/archive", response_model=ChatResponse)
def archive_chat(chat_id:int, db:Session=Depends(get_db), user: User = Depends(get_current_user)):
    archived_chat =  archive_the_chat_service(db,chat_id,user.uid)
    return archived_chat

#route to unarchive a specific chat
@router.put("/{chat_id}/unarchive", response_model=ChatResponse)
def unarchive_chat(chat_id:int, db:Session=Depends(get_db), user: User = Depends(get_current_user)):
    unarchived_chat =  unarchive_the_chat_service(db,chat_id,user.uid)
    return unarchived_chat

#route to fetch all archive chats
@router.get("/archive", response_model=List[ChatResponse])
def all_archive_chats(db:Session=Depends(get_db), user:User =Depends(get_current_user)):
    all_archive = fetch_all_archive_chats_service(db,user.uid)
    return all_archive

#route to delete all archive chats
@router.delete("/archive")
def delete_all_archive_chats(db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    count = delete_all_archive_chats_service(db, user.uid)
    if count == 0:
        return {"message": "No archived chats to delete"}
    return {"message": f"{count} archived chats deleted successfully"}

#route to delete all active and archive chats
@router.delete("/all/delete")
def delete_all_chats(db:Session=Depends(get_db), user:User=Depends(get_current_user)):
    count = delete_all_chats_service(db,user.uid)
    if count == 0:
        return {"message": "No chats to delete"}
    return {"message": f"{count} chats deleted successfully"}



