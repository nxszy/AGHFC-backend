from typing import Any

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from firebase_admin import firestore  # type: ignore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.database import get_database_ref
from app.models.collection_names import CollectionNames
from app.models.order import PanelOrdersPayload, PersistedOrder, Order
from app.models.user import UserRole
from app.services.shared.request_handler import handle_request_errors
from app.services.shared.user_role_handler import role_required

router = APIRouter(
    prefix="/order/panel",
    tags=["admin panel orders"],
)


@handle_request_errors
@router.get("/all")
async def all_orders(filters: PanelOrdersPayload,
                     dep: Any = Depends(role_required(UserRole.ADMIN)),
                     db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    order_docs = db_ref.collection(CollectionNames.ORDERS)

    if filters.restaurant_id is not None:
        restaurant_ref = db_ref.collection(CollectionNames.RESTAURANTS).document(filters.restaurant_id)
        order_docs = order_docs.where(filter=FieldFilter('restaurant_id', '==', restaurant_ref))
    if filters.status is not None:
        order_docs = order_docs.where(filter=FieldFilter('status', '==', filters.status))

    result = []

    for doc in order_docs.stream():
        persisted_order = PersistedOrder(**doc.to_dict())
        persisted_order_dict = persisted_order.model_dump()
        persisted_order_dict["restaurant_id"] = persisted_order_dict["restaurant_id"].id
        result.append(Order(**persisted_order_dict, id=doc.id).model_dump())

    return JSONResponse(content=jsonable_encoder(result), status_code=status.HTTP_201_CREATED)


@handle_request_errors
@router.get("/single/{order_id}")
async def single_order(
        order_id: str,
        dep: Any = Depends(role_required(UserRole.ADMIN)),
        db_ref: firestore.Client = Depends(get_database_ref)) -> Response:

    doc = db_ref.collection(CollectionNames.ORDERS).document(order_id).get()
    persisted_order = PersistedOrder(**doc.to_dict())
    persisted_order_dict = persisted_order.model_dump()
    persisted_order_dict["restaurant_id"] = persisted_order_dict["restaurant_id"].id
    order = Order(**persisted_order_dict, id=doc.id)
    return JSONResponse(content=jsonable_encoder(order), status_code=status.HTTP_201_CREATED)
