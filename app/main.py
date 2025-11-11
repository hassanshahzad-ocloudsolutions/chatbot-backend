from fastapi import FastAPI
from app.database import Base, engine
from app.models import user, chat, message
from app.routers import chat

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


app.include_router(chat.router)
