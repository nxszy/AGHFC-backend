from enum import Enum
from typing import Optional

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
    special_offers: list[str] = []


class User(PersistedUser):
    id: str
