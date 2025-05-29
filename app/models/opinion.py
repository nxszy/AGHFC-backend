from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field

from app.models.firestore_ref import FirestoreRef


class OpinionCreate(BaseModel):
    restaurant_id: str
    user_id: str
    dish_id: str
    rating: int
    comment: Optional[str] = None


class Opinion(BaseModel):
    id: Optional[str] = Field(default=None, description="Firestore document ID")
    restaurant_id: Annotated[FirestoreRef, ...]
    user_id: Annotated[FirestoreRef, ...]
    dish_id: Annotated[FirestoreRef, ...]
    rating: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = Field(default=None, description="Timestamp of when the opinion was created")

    class Config:
        json_encoders = {FirestoreRef: lambda v: v.ref.id}
