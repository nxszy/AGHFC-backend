from typing import Any, Union

from fastapi import APIRouter, Depends, Response, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from firebase_admin import firestore  # type: ignore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.database import get_database_ref
from app.models.collection_names import CollectionNames
from app.models.order import PanelOrdersPayload, PersistedOrder, Order, OrderStatus, TransitionOrderStatusPayload
from app.models.user import UserRole
from app.services.orders.worker_panel import transition_order_status
from app.services.shared.request_handler import handle_request_errors
from app.services.shared.user_role_handler import role_required

router = APIRouter(
    prefix="/order/worker_panel",
    tags=["worker panel orders"],
)


@handle_request_errors
@router.get("/{order_status}/all")
async def all_orders_with_status(order_status: str,
                     request: Request,
                     dep: Any = Depends(role_required(UserRole.WORKER)),
                     db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    order_docs = db_ref.collection(CollectionNames.ORDERS)

    if request.state.user.restaurant_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Worker is not assigned to any restaurant.",
        )

    acceptable_order_statuses = [OrderStatus.PAID.value, OrderStatus.IN_PROGRESS.value, OrderStatus.READY.value]
    if order_status not in acceptable_order_statuses:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{order_status} is not acceptable order status for this endpoint. Acceptable order statuses: {acceptable_order_statuses}",
        )

    order_docs = order_docs.where(filter=FieldFilter('restaurant_id', '==', request.state.user.restaurant_id))
    order_docs = order_docs.where(filter=FieldFilter('status', '==', order_status))

    result = []

    for doc in order_docs.stream():
        persisted_order = PersistedOrder(**doc.to_dict())
        persisted_order_dict = persisted_order.model_dump()
        persisted_order_dict["restaurant_id"] = persisted_order_dict["restaurant_id"].id
        result.append(Order(**persisted_order_dict, id=doc.id).model_dump())

    return JSONResponse(content=jsonable_encoder(result), status_code=status.HTTP_201_CREATED)


@handle_request_errors
@router.post("/transition_status")
async def transition_order_to_status(
        order_data: TransitionOrderStatusPayload,
        request: Request,
        dep: Any = Depends(role_required(UserRole.WORKER)),
        db_ref: firestore.Client = Depends(get_database_ref)) -> Response:

    persisted_order = transition_order_status(order_data.id, request.state.user.restaurant_id, order_data.status, db_ref)
    persisted_order_dict = persisted_order.model_dump()
    persisted_order_dict["restaurant_id"] = persisted_order_dict["restaurant_id"].id
    db_ref.collection(CollectionNames.ORDERS).document(order_data.id).set(persisted_order.model_dump())
    order = Order(**persisted_order_dict, id=order_data.id)
    return JSONResponse(content=jsonable_encoder(order), status_code=status.HTTP_201_CREATED)
