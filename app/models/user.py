import uuid
from enum import Enum

from pydantic import BaseModel, PrivateAttr


class UserRole(str, Enum):
    ADMIN = "admin"
    WORKER = "worker"
    CUSTOMER = "customer"


class User(BaseModel):
    _id: str = PrivateAttr(default_factory=lambda: str(uuid.uuid4()))
    email: str
    role: UserRole
    restaurant_id: str
    points: int = 0
    special_offers: list[str] = []
