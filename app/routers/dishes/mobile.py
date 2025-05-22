from fastapi import APIRouter, Depends, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import firestore  # type: ignore

from app.core.database import get_database_ref
from app.models.collection_names import CollectionNames
from app.models.dish import Dish
from app.services.shared.request_handler import handle_request_errors

router = APIRouter(
    prefix="/dish/mobile",
    tags=["mobile dish"],
)


@router.get("/{restaurant_id}/available")
@handle_request_errors
async def get_available_dishes(
    restaurant_id: str,
    db_ref: firestore.Client = Depends(get_database_ref),
) -> Response:
    """Get all available dishes for a given restaurant.

    Filters to dishes where `is_available == True` and `stock_count > 0`.

    Args:
        restaurant_id (str): The ID of the restaurant.

    Returns:
        Response: FastAPI response with a list of available dishes,
                  each including its `name`, `description`, `price`,
                  plus `stock_count` and `is_available` from the join record.
    """
    restaurant_ref = db_ref.collection(CollectionNames.RESTAURANTS).document(restaurant_id)

    rd_stream = (
        db_ref.collection(CollectionNames.RESTAURANT_DISHES)
        .where("restaurant_id", "==", restaurant_ref)
        .where("is_available", "==", True)
        .where("stock_count", ">", 0)
        .stream()
    )

    result = []
    for rd_doc in rd_stream:
        rd = rd_doc.to_dict()
        dish_ref = rd["dish_id"]
        dish_doc = dish_ref.get()
        if not dish_doc.exists:
            continue

        dish_data = dish_doc.to_dict()
        dish_data['price'] = dish_data['base_price']
        dish_data['id'] = dish_doc.id
        dish_payload = {
            **jsonable_encoder(Dish(**dish_data)),
            "stock_count": rd["stock_count"],
            "is_available": rd["is_available"],
        }
        result.append(dish_payload)

    return JSONResponse(content=result, status_code=status.HTTP_200_OK)
