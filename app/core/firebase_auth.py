from functools import lru_cache
from typing import Any

import firebase_admin  # type: ignore
import jwt
import requests
from fastapi import HTTPException
from firebase_admin import credentials
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
        public_keys = get_firebase_public_keys()
        header = jwt.get_unverified_header(token)
        key_id = header.get("kid")

        if key_id not in public_keys:
            raise HTTPException(status_code=401, detail="Incorrect token.")

        decoded_token = id_token.verify_firebase_token(
            token, google_requests.Request(), settings.firebase_config.project_id
        )

        if not decoded_token:
            raise HTTPException(status_code=401, detail="Incorrect Firebase token.")

        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unable to authenticate: {str(e)}.")
