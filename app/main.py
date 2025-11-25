
from fastapi import FastAPI
from app.database import Base, engine
from app.models import user, chat, message
from app.routers import chat, subscription, webhook
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


app.include_router(chat.router)
app.include_router(subscription.router)
app.include_router(webhook.router)

# Allow frontend origin
origins = [
    os.getenv("LOCALHOST_PATH1"), #local
    os.getenv("LOCALHOST_PATH2") #network
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allow your frontend origin(s)
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers (Authorization, Content-Type, etc.)
)