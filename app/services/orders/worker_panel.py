from datetime import UTC, datetime

from fastapi import HTTPException, status
from firebase_admin import firestore  # type: ignore
from google.cloud.firestore import DocumentReference  # type: ignore

from app.models.order import OrderStatus, PersistedOrder
from app.services.orders.shared import check_order_validity_and_ownership


def transition_order_status(
    order_id: str, restaurant_ref: DocumentReference, order_status: OrderStatus, db_ref: firestore.Client
) -> PersistedOrder:
    expected_status_for_transitions = {
        OrderStatus.IN_PROGRESS.value: OrderStatus.PAID,
        OrderStatus.READY.value: OrderStatus.IN_PROGRESS,
        OrderStatus.COMPLETED.value: OrderStatus.READY,
    }

    if order_status not in expected_status_for_transitions.keys():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Incorrect state to transition {order_status.value}",
        )

    order = check_order_validity_and_ownership(order_id, expected_status_for_transitions[order_status], None, db_ref)

    if order.restaurant_id.id != restaurant_ref.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No such order with id: {order_id}",
        )

    order.status = order_status
    order.updated_at = datetime.now(UTC)

    return order
