from pydantic import BaseModel


class Dish(BaseModel):
    name: str
    description: str
    ingredients: str
    price: float
    points: int
