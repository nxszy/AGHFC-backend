from typing import Annotated, Optional

from pydantic import BaseModel, Field

from app.models.firestore_ref import FirestoreRef


class Restaurant(BaseModel):
    id: Optional[str] = Field(default=None, description="Firestore document ID")
    name: str
    city: str
    address: str
    opening_hours: str
    special_offers: list[Annotated[FirestoreRef, ...]] = []
