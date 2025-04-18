from pydantic import BaseModel


class Restaurant(BaseModel):
    name: str
    city: str
    address: str
    opening_hours: str
    special_offers: list[str] = []
