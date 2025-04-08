from fastapi import APIRouter, Response, status
from firebase_admin import db

router = APIRouter(
    prefix="/restaurant/mobile",
    tags=["mobile restaurant"],
)

db_ref = db.reference("restaurants")


@router.get("/get_all_restaurants")
async def get_all_restaurants() -> Response:
    """Get all restaurants from the database.

    Returns:
        dict: A dictionary containing all restaurants.
    """
    restaurants = db_ref.get()
    return Response(
        restaurants,
        status_code=status.HTTP_200_OK,
    )

