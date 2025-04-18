from enum import Enum

from pydantic import BaseModel


class UserRole(str, Enum):
    ADMIN = "admin"
    WORKER = "worker"
    CUSTOMER = "customer"


class User(BaseModel):
    email: str
    role: UserRole
    restaurant_id: str
    points: int = 0
    special_offers: list[str] = []
