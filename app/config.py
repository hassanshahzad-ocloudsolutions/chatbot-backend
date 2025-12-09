import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Database URL for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
# Firebase service account path
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

#OLLAMA
OLLAMA_API_URL=os.getenv("OLLAMA_API_URL")
OLLAMA_MODEL=os.getenv("OLLAMA_MODEL")
OLLAMA_TEMPERATURE=os.getenv("OLLAMA_TEMPERATURE") 

#OpenAI API
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
OPENAI_MODEL=os.getenv("OPENAI_MODEL")
OPENAI_TEMPERATURE=os.getenv("OPENAI_TEMPERATURE")

STRIPE_API_KEY = os.getenv("STRIPE_SECRET_API_KEY")

WEBHOOK_SECRET=os.getenv("WEBHOOK_SECRET")

STRIPE_SUCCESS_URL=os.getenv("STRIPE_SUCCESS_URL")
STRIPE_FAILURE_URL=os.getenv("STRIPE_FAILURE_URL")

SHARE_URL=os.getenv("SHARE_URL")