from pydantic import BaseModel
from typing import Annotated
from google.cloud.firestore import DocumentReference


class RestaurantDish(BaseModel):
    dish_id: Annotated[DocumentReference, ...]
    restaurant_id: Annotated[DocumentReference, ...]
    is_available: bool
    stock_count: int

    model_config = {
        "arbitrary_types_allowed": True
    }
