from enum import Enum


class CollectionNames(str, Enum):
    DISHES = "dishes"
    ORDERS = "orders"
    RESTAURANTS = "restaurants"
    RESTAURANT_DISHES = "restaurant_dishes"
    SPECIAL_OFFERS = "special_offers"
    USERS = "users"
    OPINIONS = "opinions"
