from datetime import datetime
from enum import Enum
from typing import Annotated, Dict, Optional

from firebase_admin import firestore  # type: ignore
from pydantic import BaseModel, NonNegativeInt, PositiveInt

from app.models.collection_names import CollectionNames
from app.models.firestore_ref import FirestoreRef
from app.models.user import User


class OrderStatus(str, Enum):
    CHECKOUT = "checkout"
    PAID = "paid"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CreateOrderPayload(BaseModel):
    order_items: Dict[str, PositiveInt]
    restaurant_id: str


class UpdateOrderPayload(BaseModel):
    id: str
    order_items: Dict[str, PositiveInt]


class PayForOrderPayload(BaseModel):
    id: str
    points: NonNegativeInt = 0
    payment_method: str


class PanelOrdersPayload(BaseModel):
    restaurant_id: Optional[str] = None
    status: Optional[OrderStatus] = None


class TransitionOrderStatusPayload(BaseModel):
    id: str
    status: OrderStatus


class PersistedOrder(BaseModel):
    user_id: str
    order_items: Dict[str, PositiveInt]
    total_price: float
    total_price_including_special_offers: float
    status: OrderStatus = OrderStatus.CHECKOUT
    points_used: NonNegativeInt = 0
    points_gained: NonNegativeInt = 0
    created_at: datetime
    updated_at: datetime
    restaurant_id: Annotated[FirestoreRef, ...]
    payment_method: str = ""

    def finalize_users_loyalty_points(
        self, user: User, loyalty_points_used: int, loyalty_points_gained: int, db_ref: firestore.Client
    ) -> None:
        if loyalty_points_used == 0:
            return
        self.points_used = min(loyalty_points_used, user.points, int(self.total_price_including_special_offers))
        user.points -= self.points_used
        user.points += loyalty_points_gained

        db_ref.collection(CollectionNames.USERS).document(user.id).update({"points": user.points})


class Order(BaseModel):
    id: Optional[str] = None
    user_id: str
    order_items: Dict[str, PositiveInt]
    total_price: float
    total_price_including_special_offers: float
    status: OrderStatus = OrderStatus.CHECKOUT
    points_used: NonNegativeInt = 0
    points_gained: NonNegativeInt = 0
    created_at: datetime
    updated_at: datetime
    restaurant_id: str
    payment_method: str = ""
