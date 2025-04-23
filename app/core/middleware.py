from typing import Any, Callable

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.database import get_database_ref
from app.core.firebase_auth import verify_firebase_token
from app.models.collection_names import CollectionNames
from app.models.user import PersistedUser, User, UserRole


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "No Bearer token. Unauthorized."})

        token = auth_header.split("Bearer ")[1]

        try:
            user = verify_firebase_token(token)
            request.state.user = self.persist_user_to_database(user)
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        response = await call_next(request)
        return response

    def persist_user_to_database(self, user: Any) -> User:
        db_ref = get_database_ref()
        user_id = user.get("user_id")
        user_doc = db_ref.collection(CollectionNames.USERS).document(user_id).get()

        if not user_doc.exists:
            persisted_user = PersistedUser(**user, role=UserRole.CUSTOMER)
            db_ref.collection(CollectionNames.USERS).document(user_id).set(persisted_user.model_dump())
            return User(**persisted_user.model_dump(), id=user_id)

        return User(**user_doc.to_dict(), id=user_id)
