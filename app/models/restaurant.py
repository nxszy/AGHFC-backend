from typing import Any, Optional

from pydantic import BaseModel, Field


class Restaurant(BaseModel):
    id: Optional[str] = Field(default=None, description="Firestore document ID")
    name: str
    city: str
    address: str
    opening_hours: str
    special_offers: Any = []
