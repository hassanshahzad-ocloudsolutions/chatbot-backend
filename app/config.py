import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Database URL for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Firebase service account path
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

# Ollama model name (if using Ollama locally)
#OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama2")

# Any other API keys, tokens, or configs
# Example: OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
