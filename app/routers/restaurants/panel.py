from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import firestore  # type: ignore

from app.core.database import get_database_ref
from app.models.collection_names import CollectionNames
from app.models.restaurant import Restaurant
from app.models.restaurant_dish import RestaurantDish
from app.services.shared.request_handler import handle_request_errors

router = APIRouter(
    prefix="/restaurant/panel",
    tags=["admin panel restaurant"],
)


@router.get("/get_restaurant_by_id/{restaurant_id}")
@handle_request_errors
async def get_restaurant_by_id(restaurant_id: str, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Get a restaurant by its ID.

    Args:
        restaurant_id (str): The ID of the restaurant.

    Returns:
        Response: FastAPI response with the restaurant data.
    """
    restaurant_doc = db_ref.collection(CollectionNames.RESTAURANTS).document(restaurant_id).get()

    if not restaurant_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    json_compatible_doc = jsonable_encoder(Restaurant(**restaurant_doc.to_dict()))

    return JSONResponse(content=json_compatible_doc, status_code=status.HTTP_200_OK)


@router.post("/add_restaurant")
@handle_request_errors
async def add_restaurant(restaurant: Restaurant, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Add a new restaurant to the database.

    Args:
        restaurant (Restaurant): The restaurant object to add.

    Returns:
        Response: FastAPI response with the added restaurant data.
    """
    restaurant_dict = restaurant.model_dump()
    db_ref.collection(CollectionNames.RESTAURANTS).add(restaurant_dict)

    return JSONResponse(content=restaurant_dict, status_code=status.HTTP_201_CREATED)


@router.put("/update_restaurant/{restaurant_id}")
@handle_request_errors
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
    restaurant_dict = restaurant.model_dump()
    db_ref.collection(CollectionNames.RESTAURANTS).document(restaurant_id).set(restaurant_dict)

    return JSONResponse(content=restaurant_dict, status_code=status.HTTP_200_OK)


@router.delete("/delete_restaurant/{restaurant_id}")
@handle_request_errors
async def delete_restaurant(restaurant_id: str, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Delete a restaurant from the database.

    Args:
        restaurant_id (str): The ID of the restaurant to delete.

    Returns:
        dict: A confirmation message.
    """
    db_ref.collection(CollectionNames.RESTAURANTS).document(restaurant_id).delete()

    return JSONResponse(content={"message": "Restaurant deleted successfully"}, status_code=status.HTTP_200_OK)


@router.put("/update_special_offers/{restaurant_id}")
@handle_request_errors
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
    db_ref.collection(CollectionNames.RESTAURANTS).document(restaurant_id).update({"special_offers": special_offers})

    return JSONResponse(content={"message": "Special offers updated successfully"}, status_code=status.HTTP_200_OK)


@router.put("/update_menu/{restaurant_id}")
@handle_request_errors
async def update_menu(
    restaurant_id: str, dish_id: str, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    restaurant_dish_dict = RestaurantDish(
        restaurant_id=restaurant_id, dish_id=dish_id, is_available=False, stock_count=0
    ).model_dump()
    db_ref.collection(CollectionNames.RESTAURANT_DISHES).add(restaurant_dish_dict)

    return JSONResponse(content={"message": "Restaurant menu updated successfully"}, status_code=status.HTTP_200_OK)
