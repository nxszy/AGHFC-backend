from pydantic import BaseModel


class SpecialOffer(BaseModel):
    dish_id: str
    new_price: float
