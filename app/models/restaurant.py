from pydantic import BaseModel


class Restaurant(BaseModel):
    name: str
    city: str
    address: str
