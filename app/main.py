from fastapi import FastAPI
from database import Base, engine
from models import user, chat, message
from routers import chat

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


app.include_router(chat.router)
