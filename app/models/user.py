from enum import Enum
from typing import Optional, Annotated
from google.cloud.firestore import DocumentReference

from pydantic import BaseModel


class UserRole(str, Enum):
    ADMIN = "admin"
    WORKER = "worker"
    CUSTOMER = "customer"

class PersistedUser(BaseModel):
    email: str
    role: UserRole
    restaurant_id: Optional[str] = None
    points: int = 0
    special_offers: list[Annotated[DocumentReference, ...]] = []

    model_config = {
        "arbitrary_types_allowed": True
    }

class User(PersistedUser):
    id: str
