from functools import lru_cache
from typing import Any

import firebase_admin  # type: ignore
import jwt
import requests
from fastapi import HTTPException
from firebase_admin import auth, credentials
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.config import settings

if not firebase_admin._apps:
    cred = credentials.Certificate(settings.firebase_config.service_account_json)
    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL": settings.firebase_config.database_url,
        },
    )


@lru_cache()
def get_firebase_public_keys() -> Any:
    response = requests.get(settings.firebase_config.public_keys_url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Unable to fetch Firebase public keys.")
    return response.json()


def verify_firebase_token(token: str) -> Any:
    try:
        if jwt.get_unverified_header(token).get("kid") not in get_firebase_public_keys():
            raise HTTPException(status_code=401, detail="Incorrect token.")

        decoded_token = id_token.verify_firebase_token(
            token, google_requests.Request(), settings.firebase_config.project_id
        )

        if not decoded_token:
            raise HTTPException(status_code=401, detail="Incorrect Firebase token.")

        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unable to authenticate: {str(e)}.")


def create_firebase_user(email: str, password: str) -> str:
    try:
        user = auth.create_user(email=email, email_verified=False, password=password, disabled=False)
        return user.uid
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=400, detail=f"User with email {email} already exists in Firebase Authentication."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Firebase user: {str(e)}")


def delete_firebase_user(uid: str) -> None:
    try:
        auth.delete_user(uid)
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail=f"User with UID {uid} not found in Firebase Authentication.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete Firebase user: {str(e)}")


def change_user_password(uid: str, new_password: str) -> None:
    try:
        auth.update_user(uid, password=new_password)
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail=f"User with UID {uid} not found in Firebase Authentication.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to change user password: {str(e)}")
