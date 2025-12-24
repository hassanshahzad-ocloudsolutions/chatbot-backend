import os
import firebase_admin
from firebase_admin import credentials, auth
from app.config import FIREBASE_KEY
from fastapi import HTTPException, status
import json
from cryptography.fernet import Fernet

fernet = Fernet(FIREBASE_KEY.encode())
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # app/
file_path = os.path.join(BASE_DIR, "firebase_encrypted_credentials.txt")

with open(file_path, "rb") as f:  # binary mode
    encrypted_data = f.read()

decrypted_json_str = fernet.decrypt(encrypted_data).decode()
firebase_json = json.loads(decrypted_json_str)

# Initialize Firebase app only once
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_json)
    firebase_admin.initialize_app(cred)


def verify_firebase_token(id_token: str):
    """
    Verifies Firebase ID token and returns decoded user info (uid, email, etc.)
    Raises HTTPException if token is invalid.
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase token: {str(e)}"
        )