from pydantic import BaseModel

from typing import Annotated
from google.cloud.firestore import DocumentReference


class SpecialOffer(BaseModel):
    dish_id: Annotated[DocumentReference, ...]
    special_price: float

    model_config = {
        "arbitrary_types_allowed": True
    }
