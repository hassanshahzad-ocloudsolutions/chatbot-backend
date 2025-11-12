from fastapi import FastAPI
from app.database import Base, engine
from app.models import user, chat, message
from app.routers import chat
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


app.include_router(chat.router)


# Allow frontend origin
origins = [
    "http://localhost:8080",
    "http://192.168.0.90:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allow your frontend origin(s)
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers (Authorization, Content-Type, etc.)
)