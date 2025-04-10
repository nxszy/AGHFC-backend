from enum import Enum

from pydantic import BaseModel


class OrderStatus(str, Enum):
    CHECKOUT = "checkout"
    PAID = "paid"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(BaseModel):
    user_id: str
    restaurant_id: str
    dishes: list[str]
    total_price: float
    status: OrderStatus = OrderStatus.CHECKOUT
