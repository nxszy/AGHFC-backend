from fastapi import APIRouter, Depends, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import firestore  # type: ignore

from app.core.database import get_database_ref
from app.models.collection_names import CollectionNames
from app.models.opinion import Opinion, OpinionCreate
from app.services.shared.request_handler import handle_request_errors
from app.models.firestore_ref import FirestoreRef
from datetime import UTC, datetime

router = APIRouter(
    prefix="/opinion/mobile",
    tags=["mobile opinions"],
)


@handle_request_errors
@router.get("/get_all_opinions")
async def get_all_opinions(db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Get all opinions from the database.

    Returns:
        dict: A dictionary containing all opinions.
    """
    opinion_docs = db_ref.collection(CollectionNames.OPINIONS).stream()

    opinions = []
    for doc in opinion_docs:
        data = doc.to_dict()
        data["id"] = doc.id
        opinions.append(Opinion(**data))

    json_compatible_docs = jsonable_encoder(opinions)

    return JSONResponse(content=json_compatible_docs, status_code=status.HTTP_200_OK)


@handle_request_errors
@router.post("/add_opinion")
async def add_opinion(opinion_data: OpinionCreate, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Add an opinion with created_at and string IDs from frontend."""

    # Convert string IDs to FirestoreRef
    opinion = Opinion(
        restaurant_id=FirestoreRef(db_ref.collection(CollectionNames.RESTAURANTS).document(opinion_data.restaurant_id)),
        user_id=FirestoreRef(db_ref.collection(CollectionNames.USERS).document(opinion_data.user_id)),
        dish_id=FirestoreRef(db_ref.collection(CollectionNames.DISHES).document(opinion_data.dish_id)),
        rating=opinion_data.rating,
        comment=opinion_data.comment,
        created_at=datetime.now(UTC)
    )

    opinion_dict = opinion.model_dump(exclude={"id"})
    _, opinion_doc = db_ref.collection(CollectionNames.OPINIONS).add(opinion_dict)
    opinion_with_id = opinion.model_copy(update={"id": opinion_doc.id})

    return JSONResponse(content=jsonable_encoder(opinion_with_id), status_code=status.HTTP_201_CREATED)


@handle_request_errors
@router.put("/update_opinion")
async def update_opinion(
    opinion_id: str, opinion_data: Opinion, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    """Update an opinion.

    Returns:
        dict: A dictionary containing updated opinion
    """
    opinion_dict = opinion_data.model_dump(exclude={"id"})
    db_ref.collection(CollectionNames.OPINIONS).document(opinion_data.id).set(opinion_dict)
    opinion_with_id = opinion_data.model_copy(update={"id": opinion_id})

    return JSONResponse(content=jsonable_encoder(opinion_with_id), status_code=status.HTTP_201_CREATED)


@handle_request_errors
@router.delete("/delete_opinion/{opinion_id}")
async def delete_opinion(opinion_id: str, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    """Delete an opinion.

    Returns:
        dict: A dictionary containing deleted opinion
    """
    db_ref.collection(CollectionNames.OPINIONS).document(opinion_id).delete()

    return JSONResponse(content={"message": "Opinion deleted successfully"}, status_code=status.HTTP_200_OK)
