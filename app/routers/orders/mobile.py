from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from firebase_admin import firestore  # type: ignore

from app.core.database import get_database_ref
from app.models.collection_names import CollectionNames
from app.models.order import CreateOrderPayload, UpdateOrderPayload, OrderStatus, PersistedOrder
from app.services.orders.mobile import create_order, update_order_items
from app.services.orders.shared import check_restaurant_dishes_existence, check_order_validity_and_ownership
from app.services.restaurants.shared import check_restaurant_existence
from app.services.shared.request_handler import handle_request_errors

router = APIRouter(
    prefix="/order/mobile",
    tags=["mobile orders"],
)


@handle_request_errors
@router.post("/create")
async def create(
    order_data: CreateOrderPayload, request: Request, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    """Create an order.

    Returns:
        dict: A dictionary containing newly created order
    """


    order = create_order(order_data, request.state.user, db_ref)
    persisted_data = PersistedOrder(**order.model_dump()).model_dump()
    _, order_doc = db_ref.collection(CollectionNames.ORDERS).add(persisted_data)
    order.id = order_doc.id

    return JSONResponse(content=order.model_dump(), status_code=status.HTTP_201_CREATED)

@handle_request_errors
@router.post("/update")
async def update(
    order_data: UpdateOrderPayload,
    request: Request,
    db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    """Update an order.

    Returns:
        dict: A dictionary containing updated order
    """
    order = update_order_items(order_data, request.state.user, db_ref)
    persisted_data = PersistedOrder(**order.model_dump()).model_dump()
    db_ref.collection(CollectionNames.ORDERS).document(order_data.id).set(persisted_data)

    return JSONResponse(content=order.model_dump(), status_code=status.HTTP_201_CREATED)
