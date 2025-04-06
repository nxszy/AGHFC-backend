from pydantic import BaseModel


class StockItem(BaseModel):
    restaurant_id: str
    dish_id: str
    quantity: int
