from typing import Any

from firebase_admin import firestore  # type: ignore

from app.models.order import CreateOrderPayload, Order, OrderStatus

from .shared import calculate_order_price


def create_order(order_data: CreateOrderPayload, user: Any, db_ref: firestore.Client) -> Order:
    result_order = Order(
        user_id=user.get('user_id'),
        order_items=order_data.order_items,
        restaurant_id=order_data.restaurant_id,
        total_price=calculate_order_price(order_data, db_ref),
        status=OrderStatus.CHECKOUT,
    )

    return result_order
