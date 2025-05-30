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
    """Add a new restaurant to the database."""

    restaurant_dict = restaurant.model_dump(exclude={"id"})

    doc_ref = db_ref.collection(CollectionNames.RESTAURANTS).add(restaurant_dict)[1]

    restaurant_with_id = restaurant.model_copy(update={"id": doc_ref.id})

    return JSONResponse(content=jsonable_encoder(restaurant_with_id), status_code=status.HTTP_201_CREATED)


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
    restaurant_dict = restaurant.model_dump(exclude={"id"})

    db_ref.collection(CollectionNames.RESTAURANTS).document(restaurant_id).update(restaurant_dict)

    restaurant_with_id = restaurant.model_copy(update={"id": restaurant_id})

    return JSONResponse(content=jsonable_encoder(restaurant_with_id), status_code=status.HTTP_200_OK)


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


@router.put("/update_menu/{restaurant_id}/{dish_id}")
@handle_request_errors
async def update_menu(
    restaurant_id: str, dish_id: str, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    restaurant_ref = db_ref.collection(CollectionNames.RESTAURANTS).document(restaurant_id)

    if not restaurant_ref.get().exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    dish_ref = db_ref.collection(CollectionNames.DISHES).document(dish_id)

    if not dish_ref.get().exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")

    restaurant_dishes = (
        db_ref.collection(CollectionNames.RESTAURANT_DISHES)
        .where("restaurant_id", "==", restaurant_ref)
        .where("dish_id", "==", dish_ref)
        .get()
    )

    if restaurant_dishes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dish already in restaurant menu")

    restaurant_dish_dict = RestaurantDish(
        restaurant_id=restaurant_ref, dish_id=dish_ref, is_available=False, stock_count=0
    ).model_dump()
    db_ref.collection(CollectionNames.RESTAURANT_DISHES).add(restaurant_dish_dict)

    return JSONResponse(content={"message": "Restaurant menu updated successfully"}, status_code=status.HTTP_200_OK)
