from typing import Optional
from app.models.firestore_ref import FirestoreRef
from pydantic import BaseModel, Field


class Dish(BaseModel):
    id: Optional[str] = Field(default=None, description="Firestore document ID")
    name: str
    description: str
    ingredients: str
    price: float
    points: int

    class Config:
        json_encoders = {
            FirestoreRef: lambda v: v.ref.id
        }