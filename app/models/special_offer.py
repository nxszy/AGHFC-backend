import uuid

from pydantic import BaseModel, PrivateAttr


class SpecialOffer(BaseModel):
    _id: str = PrivateAttr(default_factory=lambda: str(uuid.uuid4()))
    dish_id: str
    new_price: float
