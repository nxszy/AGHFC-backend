import uuid
from enum import Enum

from pydantic import BaseModel, PrivateAttr


class OrderStatus(str, Enum):
    CHECKOUT = "checkout"
    PAID = "paid"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(BaseModel):
    _id: str = PrivateAttr(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    restaurant_id: str
    dishes: list[str]
    total_price: float
    status: OrderStatus = OrderStatus.CHECKOUT
