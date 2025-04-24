from typing import Annotated

from pydantic import BaseModel

from app.models.firestore_ref import FirestoreRef


class RestaurantDish(BaseModel):
    dish_id: Annotated[FirestoreRef, ...]
    restaurant_id: Annotated[FirestoreRef, ...]
    is_available: bool
    stock_count: int
