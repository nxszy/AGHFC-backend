import jwt
import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from fastapi import HTTPException
from functools import lru_cache
import firebase_admin

from app.config import settings

if not firebase_admin._apps:
    firebase_admin.initialize_app()

@lru_cache()
def get_firebase_public_keys():
    response = requests.get(settings.firebase_config.public_keys_url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unable to fetch Firebase public keys.")
    return response.json()

def verify_firebase_token(token: str):
    try:
        public_keys = get_firebase_public_keys()
        header = jwt.get_unverified_header(token)
        key_id = header.get("kid")

        if key_id not in public_keys:
            raise HTTPException(status_code=401, detail="Incorrect token.")

        decoded_token = id_token.verify_firebase_token(token, google_requests.Request(), settings.firebase_config.project_id)

        if not decoded_token:
            raise HTTPException(status_code=401, detail="Incorrect Firebase token.")

        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unable to authenticate: {str(e)}.")