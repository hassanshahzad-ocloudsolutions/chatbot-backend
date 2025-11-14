import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Database URL for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
# Firebase service account path
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

#OLLAMA
OLLAMA_API=os.getenv("OLLAMA_API_URL")
OLLAMA_MODEL=os.getenv("OLLAMA_MODEL")
OLLAMA_TEMPERATURE=os.getenv("OLLAMA_TEMPERATURE") 

#OpenAI API
OPENAI_API=os.getenv("OPENAI_API_KEY")
OPENAI_MODEL=os.getenv("OPENAI_MODEL")
OPENAI_TEMPERATURE=os.getenv("OPENAI_TEMPERATURE")


