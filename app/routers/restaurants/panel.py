import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import exceptions, firestore  # type: ignore

from app.core.database import get_database_ref
from app.models.restaurant import Restaurant
from app.models.restaurant_dish import RestaurantDish

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/restaurant/panel",
    tags=["admin panel restaurant"],
)


@router.get("/get_restaurant_by_id/{restaurant_id}")
async def get_restaurant_by_id(restaurant_id: str, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Get a restaurant by its ID.

    Args:
        restaurant_id (str): The ID of the restaurant.

    Returns:
        Response: FastAPI response with the restaurant data.
    """
    try:
        restaurant_doc = db_ref.collection("restaurants").document(restaurant_id).get()

        if not restaurant_doc.exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

        json_compatible_doc = jsonable_encoder(Restaurant(**restaurant_doc.to_dict()))

        return JSONResponse(content=json_compatible_doc, status_code=status.HTTP_200_OK)

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


@router.post("/add_restaurant")
async def add_restaurant(restaurant: Restaurant, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Add a new restaurant to the database.

    Args:
        restaurant (Restaurant): The restaurant object to add.

    Returns:
        Response: FastAPI response with the added restaurant data.
    """
    try:
        restaurant_dict = restaurant.model_dump()
        db_ref.collection("restaurants").add(restaurant_dict)

        return JSONResponse(content=restaurant_dict, status_code=status.HTTP_201_CREATED)

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


@router.put("/update_restaurant/{restaurant_id}")
async def update_restaurant(
    restaurant_id: str, restaurant: Restaurant, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    """Update an existing restaurant in the database.

    Args:
        restaurant_id (str): The ID of the restaurant to update.
        restaurant (Restaurant): The updated restaurant object.

    Returns:
        Response: FastAPI response with the updated restaurant data.
    """
    try:
        restaurant_dict = restaurant.model_dump()
        db_ref.collection("restaurants").document(restaurant_id).set(restaurant_dict)

        return JSONResponse(content=restaurant_dict, status_code=status.HTTP_200_OK)

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


@router.delete("/delete_restaurant/{restaurant_id}")
async def delete_restaurant(restaurant_id: str, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Delete a restaurant from the database.

    Args:
        restaurant_id (str): The ID of the restaurant to delete.

    Returns:
        dict: A confirmation message.
    """
    try:
        db_ref.collection("restaurants").document(restaurant_id).delete()

        return JSONResponse(content={"message": "Restaurant deleted successfully"}, status_code=status.HTTP_200_OK)

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


@router.put("/update_special_offers/{restaurant_id}")
async def update_special_offers(
    restaurant_id: str, special_offers: list[str], db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    """Update the special offers for a restaurant.

    Args:
        restaurant_id (str): The ID of the restaurant.
        special_offers (list[str]): The updated list of special offers ids (refs).

    Returns:
        dict: A confirmation message.
    """
    try:
        db_ref.collection("restaurants").document(restaurant_id).update({"special_offers": special_offers})

        return JSONResponse(content={"message": "Special offers updated successfully"}, status_code=status.HTTP_200_OK)

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


@router.put("/update_menu/{restaurant_id}")
async def update_menu(
    restaurant_id: str, dish_id: str, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    try:
        restaurant_dish_dict = RestaurantDish(
            restaurant_id=restaurant_id, dish_id=dish_id, is_available=False, stock_count=0
        ).model_dump()
        db_ref.collection("restaurant_dishes").add(restaurant_dish_dict)

        return JSONResponse(content={"message": "Restaurant menu updated successfully"}, status_code=status.HTTP_200_OK)

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
