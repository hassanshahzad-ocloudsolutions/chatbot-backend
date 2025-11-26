from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from openai import OpenAI
from app.config import OPENAI_API_KEY
import os
from app.services.chatbot_service import OpenAi


router = APIRouter(prefix="/transcriptions")

@router.post("/record_transcribe")
async def record_transcribe(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Accepts an audio file recorded from user mic (mp3, webm, wav),
    sends it to OpenAI Whisper API, and returns the transcription.
    """
    # Optional: support multiple formats from mic
    allowed_extensions = (".mp3", ".wav", ".webm", ".ogg")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail=f"Unsupported audio format. Allowed: {allowed_extensions}")

    text = await OpenAi().transcribe_audio(file)
    
    return {"transcription": text}


