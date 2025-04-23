
from typing import Any, Annotated, Optional

from pydantic import BaseModel, Field

from google.cloud.firestore import DocumentReference  # type: ignore


class Restaurant(BaseModel):
    id: Optional[str] = Field(default=None, description="Firestore document ID")
    name: str
    city: str
    address: str
    opening_hours: str
    special_offers: list[Annotated[DocumentReference, ...]] = []

    model_config = {"arbitrary_types_allowed": True}
