from typing import Annotated

from google.cloud.firestore import DocumentReference  # type: ignore
from pydantic import BaseModel


class SpecialOffer(BaseModel):
    dish_id: Annotated[DocumentReference, ...]
    special_price: float

    model_config = {"arbitrary_types_allowed": True}
