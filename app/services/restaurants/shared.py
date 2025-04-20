from fastapi import HTTPException, status
from firebase_admin import firestore  # type: ignore

from app.models.collection_names import CollectionNames
from google.cloud.firestore import DocumentReference


def check_restaurant_existence(restaurant_id: str, db_ref: firestore.Client) -> DocumentReference:
    restaurant_doc = db_ref.collection(CollectionNames.RESTAURANTS).document(restaurant_id).get()

    if not restaurant_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Incorrect restaurant id: {restaurant_id}"
        )

    return restaurant_doc.reference