from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import firestore  # type: ignore
from pydantic import BaseModel

from app.core.database import get_database_ref
from app.models.collection_names import CollectionNames
from app.services.shared.request_handler import handle_request_errors

router = APIRouter(
    prefix="/restaurant_dish/panel",
    tags=["admin panel restaurant dish"],
)


class RestaurantDishStateUpdate(BaseModel):
    """New availability flag and stock count for a dish in a restaurant."""
    is_available: bool
    stock_count: int


@router.patch("/{restaurant_id}/{dish_id}")
@handle_request_errors
async def update_restaurant_dish_state(
    restaurant_id: str,
    dish_id: str,
    state: RestaurantDishStateUpdate,
    db_ref: firestore.Client = Depends(get_database_ref),
) -> Response:
    """Update availability and stock count for a specific dish in a restaurant.

    Args:
        restaurant_id (str): The ID of the restaurant.
        dish_id (str): The ID of the dish.
        state (RestaurantDishStateUpdate): New availability flag and stock count.

    Returns:
        Response: FastAPI response with a confirmation message.
    """
    restaurant_ref = db_ref.collection(CollectionNames.RESTAURANTS).document(restaurant_id)
    dish_ref = db_ref.collection(CollectionNames.DISHES).document(dish_id)

    coll = db_ref.collection(CollectionNames.RESTAURANT_DISHES)
    query = (
        coll
        .where("restaurant_id", "==", restaurant_ref)
        .where("dish_id", "==", dish_ref)
        .limit(1)
        .get()
    )

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not assigned to this restaurant"
        )

    entry_ref = query[0].reference
    entry_ref.update({
        "is_available": state.is_available,
        "stock_count": state.stock_count
    })

    return JSONResponse(
        content={"message": "Restaurant–dish state updated successfully"},
        status_code=status.HTTP_200_OK
    )
