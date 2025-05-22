from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import firestore  # type: ignore

from app.core.database import get_database_ref
from app.models.collection_names import CollectionNames
from app.models.dish import Dish
from app.services.shared.request_handler import handle_request_errors

router = APIRouter(
    prefix="/dish/panel",
    tags=["admin panel dish"],
)


@router.get("/get_dish_by_id/{dish_id}")
@handle_request_errors
async def get_dish_by_id(dish_id: str, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Get a dish by its ID.

    Args:
        dish_id (str): The ID of the dish.

    Returns:
        Response: FastAPI response with the dish data.
    """
    doc = db_ref.collection(CollectionNames.DISHES).document(dish_id).get()
    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
    data = doc.to_dict()
    data["price"] = data.pop("base_price")
    dish = Dish(**data)
    return JSONResponse(content=jsonable_encoder(dish), status_code=status.HTTP_200_OK)


@router.get("/list_dishes")
@handle_request_errors
async def list_dishes(db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """List all dishes in the database.

    Returns:
        Response: FastAPI response with a list of all dishes.
    """
    docs = db_ref.collection(CollectionNames.DISHES).get()
    dishes = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        dishes.append(data)
    return JSONResponse(content=jsonable_encoder(dishes), status_code=status.HTTP_200_OK)


@router.post("/add_dish")
@handle_request_errors
async def add_dish(dish: Dish, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Add a new dish to the database.

    Args:
        dish (Dish): The dish object to add.

    Returns:
        Response: FastAPI response with the added dish data, including generated ID.
    """
    dish_dict = dish.model_dump(exclude={"id"})
    write_time, doc_ref = db_ref.collection(CollectionNames.DISHES).add(dish_dict)
    created = {**dish_dict, "id": doc_ref.id}
    return JSONResponse(content=jsonable_encoder(created), status_code=status.HTTP_201_CREATED)


@router.put("/update_dish/{dish_id}")
@handle_request_errors
async def update_dish(dish_id: str, dish: Dish, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Update an existing dish in the database.

    Args:
        dish_id (str): The ID of the dish to update.
        dish (Dish): The updated dish object.

    Returns:
        Response: FastAPI response with the updated dish data.
    """
    dish_dict = dish.model_dump()
    doc_ref = db_ref.collection(CollectionNames.DISHES).document(dish_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
    doc_ref.set(dish_dict)
    return JSONResponse(content=jsonable_encoder(dish_dict), status_code=status.HTTP_200_OK)


@router.delete("/delete_dish/{dish_id}")
@handle_request_errors
async def delete_dish(dish_id: str, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Delete a dish from the database.

    Args:
        dish_id (str): The ID of the dish to delete.

    Returns:
        Response: FastAPI response with a confirmation message.
    """
    doc_ref = db_ref.collection(CollectionNames.DISHES).document(dish_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
    doc_ref.delete()
    return JSONResponse(content={"message": "Dish deleted successfully"}, status_code=status.HTTP_200_OK)
