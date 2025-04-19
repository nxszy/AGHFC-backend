from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel


class OrderStatus(str, Enum):
    CHECKOUT = "checkout"
    PAID = "paid"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CreateOrderPayload(BaseModel):
    order_items: Dict[str, int]
    restaurant_id: str

class UpdateOrderPayload(BaseModel):
    id: str
    order_items: Dict[str, int]

class PersistedOrder(CreateOrderPayload):
    user_id: str
    total_price: float
    status: OrderStatus = OrderStatus.CHECKOUT

class Order(PersistedOrder):
    id: Optional[str] = None

