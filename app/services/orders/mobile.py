from typing import Any
from datetime import datetime

from firebase_admin import firestore  # type: ignore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.models.order import CreateOrderPayload, Order, OrderStatus, UpdateOrderPayload
from app.models.user import User
from app.models.collection_names import CollectionNames

from .shared import calculate_order_price, check_restaurant_dishes_existence, check_order_validity_and_ownership
from app.services.restaurants.shared import check_restaurant_existence


def create_order(order_data: CreateOrderPayload, user: User, db_ref: firestore.Client) -> Order:
    check_restaurant_existence(order_data.restaurant_id, db_ref)
    check_restaurant_dishes_existence(order_data, db_ref)
    now = datetime.utcnow()

    result_order = Order(
        user_id=user.id,
        order_items=order_data.order_items,
        restaurant_id=order_data.restaurant_id,
        total_price=calculate_order_price(order_data.order_items, db_ref),
        status=OrderStatus.CHECKOUT,
        created_at=now,
        updated_at=now,
    )

    return result_order

def update_order_items(order_data: UpdateOrderPayload, user: User, db_ref: firestore.Client):
    order = check_order_validity_and_ownership(order_data.id,
                                       OrderStatus.CHECKOUT,
                                       user,
                                       db_ref)
    check_restaurant_dishes_existence(
        CreateOrderPayload(**order_data.model_dump(),
                           restaurant_id=order.restaurant_id),
        db_ref
    )

    order.id = order_data.id
    order.order_items = order_data.order_items
    order.total_price = calculate_order_price(order.order_items, db_ref)
    order.updated_at = datetime.utcnow()
    return order

def users_order_history(user: User, db_ref: firestore.Client):
    order_docs = (
        db_ref.collection(CollectionNames.ORDERS)
        .where(filter=FieldFilter("user_id", "==", user.id))
        .where(filter=FieldFilter("status", "!=", OrderStatus.CHECKOUT))
        .stream()
    )

    return [ Order(**doc.to_dict(), id=doc.id) for doc in order_docs ]
