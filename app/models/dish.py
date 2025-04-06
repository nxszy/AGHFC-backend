import uuid

from pydantic import BaseModel, PrivateAttr


class Dish(BaseModel):
    _id: str = PrivateAttr(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
