import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("API_KEY")  # "API_KEY" is the name in your .env
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
payload = {
    "email": EMAIL,
    "password": PASSWORD,
    "returnSecureToken": True
}

response = requests.post(url, json=payload)
data = response.json()
print("ID Token:", data.get("idToken"))
