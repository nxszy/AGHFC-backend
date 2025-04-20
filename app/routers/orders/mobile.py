from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import firestore  # type: ignore

from app.core.database import get_database_ref
from app.models.collection_names import CollectionNames
from app.models.order import CreateOrderPayload, UpdateOrderPayload, OrderStatus, PersistedOrder, PayForOrderPayload, Order

from app.services.orders.mobile import create_order, update_order_items, users_order_history
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


    persisted_order = create_order(order_data, request.state.user, db_ref)
    persisted_order_dict = persisted_order.model_dump()
    persisted_order_dict['restaurant_id'] = persisted_order_dict['restaurant_id'].id
    order = Order(**persisted_order_dict)
    _, order_doc = db_ref.collection(CollectionNames.ORDERS).add(persisted_order.model_dump())
    order.id = order_doc.id

    return JSONResponse(content=jsonable_encoder(order.model_dump()), status_code=status.HTTP_201_CREATED)

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
    persisted_order = update_order_items(order_data, request.state.user, db_ref)
    persisted_order_dict = persisted_order.model_dump()
    persisted_order_dict['restaurant_id'] = persisted_order_dict['restaurant_id'].id
    order = Order(**persisted_order_dict, id=order_data.id)
    db_ref.collection(CollectionNames.ORDERS).document(order_data.id).set(persisted_order.model_dump())

    return JSONResponse(content=jsonable_encoder(order.model_dump()), status_code=status.HTTP_201_CREATED)

@handle_request_errors
@router.get("/history")
async def get_users_order_history(
    request: Request,
    db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    """Get users order history

    Returns:
        dict[]: a list of orders made by authenticated user, that are in different state than checkout
    """
    orders = users_order_history(request.state.user, db_ref)

    return JSONResponse(content=[jsonable_encoder(order.model_dump()) for order in orders], status_code=status.HTTP_201_CREATED)

@handle_request_errors
@router.get("/{order_id}")
async def get_single_order(
    order_id: str,
    request: Request,
    db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    """Get a single order.

    Returns:
        dict: A dictionary containing order with specified order id
    """
    persisted_order = check_order_validity_and_ownership(order_id, None, request.state.user, db_ref)
    persisted_order_dict = persisted_order.model_dump()
    persisted_order_dict['restaurant_id'] = persisted_order_dict['restaurant_id'].id
    order = Order(**persisted_order_dict, id=order_id)

    return JSONResponse(content=jsonable_encoder(order.model_dump()), status_code=status.HTTP_201_CREATED)
