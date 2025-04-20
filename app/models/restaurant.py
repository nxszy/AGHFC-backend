from pydantic import BaseModel
from typing import Annotated
from google.cloud.firestore import DocumentReference


class Restaurant(BaseModel):
    name: str
    city: str
    address: str
    opening_hours: str
    special_offers: list[Annotated[DocumentReference, ...]] = []

    model_config = {
        "arbitrary_types_allowed": True
    }
