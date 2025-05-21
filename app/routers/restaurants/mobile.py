from fastapi import APIRouter, Depends, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import firestore  # type: ignore

from app.core.database import get_database_ref
from app.models.collection_names import CollectionNames
from app.models.restaurant import Restaurant
from app.services.shared.request_handler import handle_request_errors

router = APIRouter(
    prefix="/restaurant/mobile",
    tags=["mobile restaurant"],
)


@router.get("/get_all_restaurants")
@handle_request_errors
async def get_all_restaurants(db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Get all restaurants from the database.

    Returns:
        dict: A dictionary containing all restaurants.
    """
    restaurant_docs = db_ref.collection(CollectionNames.RESTAURANTS).stream()

    restaurants = []
    for doc in restaurant_docs:
        data = doc.to_dict()
        data['id'] = doc.id
        restaurants.append(Restaurant(**data))

    json_compatible_docs = jsonable_encoder(restaurants)

    return JSONResponse(content=json_compatible_docs, status_code=status.HTTP_200_OK)
