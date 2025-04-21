from typing import Any
from datetime import datetime

from firebase_admin import firestore  # type: ignore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.models.order import CreateOrderPayload, Order, OrderStatus, UpdateOrderPayload, PayForOrderPayload, \
    PersistedOrder
from app.models.user import User
from app.models.collection_names import CollectionNames

from .shared import calculate_order_prices, check_restaurant_dishes_existence, check_order_validity_and_ownership, \
    get_order_by_id, finalize_order_stock
from app.services.restaurants.shared import check_restaurant_existence


def create_order(order_data: CreateOrderPayload, user: User, db_ref: firestore.Client) -> PersistedOrder:
    restaurant_reference = check_restaurant_existence(order_data.restaurant_id, db_ref)
    check_restaurant_dishes_existence(order_data, db_ref)
    now = datetime.utcnow()

    result_order = PersistedOrder(
        user_id=user.id,
        order_items=order_data.order_items,
        restaurant_id=restaurant_reference,
        total_price=0,
        total_price_including_special_offers=0,
        status=OrderStatus.CHECKOUT,
        created_at=now,
        updated_at=now,
    )
    (
        result_order.total_price,
        result_order.total_price_including_special_offers
    ) = calculate_order_prices(result_order, user, db_ref)

    return result_order


def update_order_items(order_data: UpdateOrderPayload, user: User, db_ref: firestore.Client) -> PersistedOrder:
    order = check_order_validity_and_ownership(order_data.id,
                                               OrderStatus.CHECKOUT,
                                               user,
                                               db_ref)
    check_restaurant_dishes_existence(
        CreateOrderPayload(**order_data.model_dump(),
                           restaurant_id=order.restaurant_id.id),
        db_ref
    )

    order.order_items = order_data.order_items
    order.total_price, order.total_price_including_special_offers = calculate_order_prices(order, user, db_ref)
    order.updated_at = datetime.utcnow()
    return order


def users_order_history(user: User, db_ref: firestore.Client):
    order_docs = (
        db_ref.collection(CollectionNames.ORDERS)
        .where(filter=FieldFilter("user_id", "==", user.id))
        .where(filter=FieldFilter("status", "!=", OrderStatus.CHECKOUT))
        .stream()
    )

    return [
        Order(**(lambda d: d.update({'restaurant_id': d['restaurant_id'].id}) or d)(doc.to_dict()),
              id=doc.id)
        for doc in order_docs
    ]

def transition_order_to_payment(order_data: PayForOrderPayload, user: User, db_ref: firestore.Client):
    order = check_order_validity_and_ownership(order_data.id, OrderStatus.CHECKOUT, user, db_ref)

    if len(order.order_items) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot pay for empty order with id: {order_id}.",
        )
    order.total_price, order.total_price_including_special_offers = calculate_order_prices(order, user, db_ref)
    finalize_order_stock(order, order_data.id, db_ref)
    order.status = OrderStatus.PAID
    order.updated_at = datetime.utcnow()

    return order


