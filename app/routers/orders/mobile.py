from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from firebase_admin import firestore  # type: ignore

from app.core.database import get_database_ref
from app.models.collection_names import CollectionNames
from app.models.order import CreateOrderPayload
from app.services.orders.mobile import create_order
from app.services.orders.shared import check_restaurant_dishes_existence
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
    check_restaurant_existence(order_data.restaurant_id, db_ref)
    check_restaurant_dishes_existence(order_data, db_ref)

    order = create_order(order_data, request.state.user, db_ref)
    order_dict = order.model_dump()
    db_ref.collection(CollectionNames.ORDERS).add(order_dict)

    return JSONResponse(content=order_dict, status_code=status.HTTP_201_CREATED)
