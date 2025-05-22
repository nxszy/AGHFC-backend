from typing import Annotated

from pydantic import BaseModel

from app.models.firestore_ref import FirestoreRef


class SpecialOffer(BaseModel):
    dish_id: Annotated[FirestoreRef, ...]
    name: str
    special_price: float
