from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel

from app.models.firestore_ref import FirestoreRef


class UserRole(str, Enum):
    ADMIN = "admin"
    WORKER = "worker"
    CUSTOMER = "customer"


class PersistedUser(BaseModel):
    email: str
    role: UserRole
    restaurant_id: Optional[Annotated[FirestoreRef, ...]] = None
    points: int = 0
    special_offers: list[Annotated[FirestoreRef, ...]] = []


class User(PersistedUser):
    id: str

class DisplayedUser(BaseModel):
    id: str
    email: str
    points: int
