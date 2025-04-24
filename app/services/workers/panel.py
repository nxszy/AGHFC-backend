import random
import string

from fastapi import HTTPException, status
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.firebase_auth import change_user_password, create_firebase_user, delete_firebase_user
from app.models.collection_names import CollectionNames
from app.models.user import PersistedUser, UserRole
from app.services.restaurants.shared import check_restaurant_existence


def get_all_workers(db_ref: firestore.Client) -> list[dict]:
    workers_docs = (
        db_ref.collection(CollectionNames.USERS).where(filter=FieldFilter("role", "==", UserRole.WORKER)).stream()
    )
    result = []

    for doc in workers_docs:
        worker_data = doc.to_dict()
        restaurant_id = None
        restaurant_name = None

        if worker_data.get("restaurant_id"):
            restaurant_ref = worker_data.get("restaurant_id")
            restaurant_id = restaurant_ref.id
            restaurant_doc = restaurant_ref.get()
            if restaurant_doc.exists:
                restaurant_name = restaurant_doc.to_dict().get("name")

        result.append(
            {
                "id": doc.id,
                "email": worker_data.get("email"),
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
            }
        )

    return result


def get_worker_by_id(worker_id: str, db_ref: firestore.Client) -> dict:
    worker_doc = db_ref.collection(CollectionNames.USERS).document(worker_id).get()

    if not worker_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Worker with id {worker_id} not found")

    worker_data = worker_doc.to_dict()

    if worker_data.get("role") != UserRole.WORKER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with id {worker_id} is not a worker")

    restaurant_id = None
    restaurant_name = None

    if worker_data.get("restaurant_id"):
        restaurant_ref = worker_data.get("restaurant_id")
        restaurant_id = restaurant_ref.id
        restaurant_doc = restaurant_ref.get()
        if restaurant_doc.exists:
            restaurant_name = restaurant_doc.to_dict().get("name")

    return {
        "id": worker_doc.id,
        "email": worker_data.get("email"),
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant_name,
    }


def generate_secure_password() -> str:
    length = 16
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*()-_=+[]{}|;:,.<>?"

    password = [random.choice(lowercase), random.choice(uppercase), random.choice(digits), random.choice(special)]

    all_chars = lowercase + uppercase + digits + special
    password.extend(random.choice(all_chars) for _ in range(length - len(password)))
    random.shuffle(password)

    return "".join(password)


def create_worker(email: str, password: str, db_ref: firestore.Client) -> dict:
    if db_ref.collection(CollectionNames.USERS).where(filter=FieldFilter("email", "==", email)).limit(1).get():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email {email} already exists")

    firebase_user_uid = create_firebase_user(email, password)

    db_ref.collection(CollectionNames.USERS).document(firebase_user_uid).set(
        PersistedUser(email=email, role=UserRole.WORKER).model_dump()
    )

    return {
        "id": firebase_user_uid,
        "email": email,
        "restaurant_id": None,
        "restaurant_name": None,
        "password": password,
    }


def assign_worker_to_restaurant(worker_id: str, restaurant_id: str, db_ref: firestore.Client) -> dict:
    worker_doc = db_ref.collection(CollectionNames.USERS).document(worker_id).get()

    if not worker_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Worker with id {worker_id} not found")

    worker_data = worker_doc.to_dict()

    if worker_data.get("role") != UserRole.WORKER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with id {worker_id} is not a worker")

    restaurant_ref = check_restaurant_existence(restaurant_id, db_ref)

    db_ref.collection(CollectionNames.USERS).document(worker_id).update({"restaurant_id": restaurant_ref})

    restaurant_doc = restaurant_ref.get()
    restaurant_name = restaurant_doc.to_dict().get("name")

    return {
        "id": worker_id,
        "email": worker_data.get("email"),
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant_name,
    }


def remove_worker_from_restaurant(worker_id: str, db_ref: firestore.Client) -> dict:
    worker_doc = db_ref.collection(CollectionNames.USERS).document(worker_id).get()

    if not worker_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Worker with id {worker_id} not found")

    worker_data = worker_doc.to_dict()

    if worker_data.get("role") != UserRole.WORKER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with id {worker_id} is not a worker")

    if not worker_data.get("restaurant_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Worker with id {worker_id} is not assigned to any restaurant",
        )

    db_ref.collection(CollectionNames.USERS).document(worker_id).update({"restaurant_id": None})

    return {
        "id": worker_id,
        "email": worker_data.get("email"),
        "restaurant_id": None,
        "restaurant_name": None,
    }


def delete_worker(worker_id: str, db_ref: firestore.Client) -> dict:
    worker_doc = db_ref.collection(CollectionNames.USERS).document(worker_id).get()

    if not worker_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Worker with id {worker_id} not found")

    worker_data = worker_doc.to_dict()

    if worker_data.get("role") != UserRole.WORKER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with id {worker_id} is not a worker")

    delete_firebase_user(worker_id)

    db_ref.collection(CollectionNames.USERS).document(worker_id).delete()

    return {"message": f"Worker with id {worker_id} deleted successfully"}


def change_worker_password(worker_id: str, new_password: str, db_ref: firestore.Client) -> dict:
    worker_doc = db_ref.collection(CollectionNames.USERS).document(worker_id).get()

    if not worker_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Worker with id {worker_id} not found")

    worker_data = worker_doc.to_dict()

    if worker_data.get("role") != UserRole.WORKER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with id {worker_id} is not a worker")

    change_user_password(worker_id, new_password)

    return {"message": "Password changed successfully"}
