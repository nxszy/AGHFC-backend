from fastapi import HTTPException, status
from firebase_admin import firestore  # type: ignore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.models.collection_names import CollectionNames
from app.models.order import CreateOrderPayload


def calculate_order_price(order: CreateOrderPayload, db_ref: firestore.Client) -> float:
    order_items = order.order_items
    dish_ids = list(order_items.keys())
    dish_refs = [db_ref.collection(CollectionNames.DISHES).document(dish_id) for dish_id in dish_ids]

    dishes_docs = db_ref.get_all(dish_refs)

    order_total = float(sum([order_items[dish.id] * dish.to_dict().get("base_price") for dish in dishes_docs]))
    return order_total


def check_restaurant_dishes_existence(order: CreateOrderPayload, db_ref: firestore.Client) -> None:
    restaurant_id = order.restaurant_id
    dish_ids = list(order.order_items.keys())
    dish_refs = [db_ref.collection(CollectionNames.DISHES).document(dish_id) for dish_id in dish_ids]
    restaurant_ref = db_ref.collection(CollectionNames.RESTAURANTS).document(restaurant_id)

    restaurant_dishes_docs = (
        db_ref.collection(CollectionNames.RESTAURANT_DISHES)
        .where(filter=FieldFilter("dish_id", "in", dish_refs))
        .where(filter=FieldFilter("restaurant_id", "==", restaurant_ref))
        .stream()
    )

    restaurant_dishes_ids = [doc.to_dict().get("dish_id").id for doc in restaurant_dishes_docs]
    incorrect_dishes_ids = list(set(dish_ids).difference(set(restaurant_dishes_ids)))

    if len(incorrect_dishes_ids) > 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Incorrect dish ids {incorrect_dishes_ids} - did not found dishes with those ids in specified restaurant",
        )
