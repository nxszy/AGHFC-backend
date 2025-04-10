import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import exceptions, firestore  # type: ignore

from app.core.database import get_database_ref
from app.models.restaurant import Restaurant

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/restaurant/mobile",
    tags=["mobile restaurant"],
)


@router.get("/get_all_restaurants")
async def get_all_restaurants(db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Get all restaurants from the database.

    Returns:
        dict: A dictionary containing all restaurants.
    """
    try:
        restaurant_docs = db_ref.collection("restaurants").stream()

        json_compatible_docs = jsonable_encoder([Restaurant(**doc.to_dict()) for doc in restaurant_docs])

        return JSONResponse(content=json_compatible_docs, status_code=status.HTTP_200_OK)

    except exceptions.FirebaseError as e:
        logger.error(f"Firebase error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to connect to Firestore database"
        )

    except ValueError as e:
        logger.error(f"Data conversion error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error processing data from Firestore")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
