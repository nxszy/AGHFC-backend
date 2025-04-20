from enum import Enum
from typing import Dict, Optional, Annotated

from datetime import datetime

from pydantic import BaseModel, NonNegativeInt
from google.cloud.firestore import DocumentReference


class OrderStatus(str, Enum):
    CHECKOUT = "checkout"
    PAID = "paid"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CreateOrderPayload(BaseModel):
    order_items: Dict[str, NonNegativeInt]
    restaurant_id: str

class UpdateOrderPayload(BaseModel):
    id: str
    order_items: Dict[str, int]

class PayForOrderPayload(BaseModel):
    id: str
    points: NonNegativeInt = 0

class PersistedOrder(BaseModel):
    user_id: str
    order_items: Dict[str, NonNegativeInt]
    total_price: float
    total_price_including_special_offers: float
    status: OrderStatus = OrderStatus.CHECKOUT
    points_used: NonNegativeInt = 0
    created_at: datetime
    updated_at: datetime
    restaurant_id: Annotated[DocumentReference, ...]

    model_config = {
        "arbitrary_types_allowed": True
    }

class Order(PersistedOrder):
    id: Optional[str] = None
    restaurant_id: str

