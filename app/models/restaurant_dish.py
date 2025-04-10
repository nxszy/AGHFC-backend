from pydantic import BaseModel


class RestaurantDish(BaseModel):
    dish_id: str
    restaurant_id: str
    is_available: bool
    stock_count: int
