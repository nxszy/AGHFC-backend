from typing import Optional

from pydantic import BaseModel, Field


class Dish(BaseModel):
    id: Optional[str] = Field(default=None, description="Firestore document ID")
    name: str
    description: str
    ingredients: str
    price: float
    points: int
