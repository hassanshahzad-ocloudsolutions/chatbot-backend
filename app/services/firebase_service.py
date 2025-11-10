import firebase_admin
from firebase_admin import credentials, auth
from config import FIREBASE_CREDENTIALS
from fastapi import HTTPException, status
import json

#testing 

firebase_json = json.loads(FIREBASE_CREDENTIALS)  


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