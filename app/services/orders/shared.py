from typing import Any, Dict

from fastapi import HTTPException, status
from firebase_admin import firestore  # type: ignore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.models.collection_names import CollectionNames
from app.models.order import CreateOrderPayload, OrderStatus, Order, PersistedOrder
from app.models.special_offer import SpecialOffer
from app.models.user import User


def calculate_order_prices(order:Order, user:User, db_ref: firestore.Client) -> float:
    order_items = order.order_items
    dish_ids = list(order_items.keys())
    dish_refs = [db_ref.collection(CollectionNames.DISHES).document(dish_id) for dish_id in dish_ids]

    dishes_docs = db_ref.get_all(dish_refs)

    order_total = float(sum([order_items[dish.id] * dish.to_dict().get("base_price") for dish in dishes_docs]))
    return order_total


def check_restaurant_dishes_existence(order: CreateOrderPayload, db_ref: firestore.Client) -> None:
    restaurant_id = order.restaurant_id
    dish_ids = list(order.order_items.keys())

    if len(dish_ids) == 0:
        return

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


def check_order_validity_and_ownership(order_id: str,
                                       expected_state: OrderStatus | None,
                                       current_user: User,
                                       db_ref: firestore.Client) -> PersistedOrder:
    order_doc = db_ref.collection(CollectionNames.ORDERS).document(order_id).get()
    order_dict = order_doc.to_dict() if order_doc.exists else None
    user_id = current_user.id

    if not order_doc.exists or order_dict.get('user_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No such order with id: {order_id}",
        )

    if expected_state is not None and order_dict.get('state') == expected_state:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot process order with id: {order_id} - incorrect state: {order_dict.get('state')}, expected state: {expected_state}",
        )

    return PersistedOrder(**order_dict, id=order_id)
