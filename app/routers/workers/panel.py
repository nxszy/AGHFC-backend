from fastapi import APIRouter, Depends, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import firestore  # type: ignore
from pydantic import BaseModel, EmailStr

from app.core.database import get_database_ref
from app.models.user import UserRole
from app.services.shared.request_handler import handle_request_errors
from app.services.shared.user_role_handler import role_required
from app.services.workers.panel import (
    assign_worker_to_restaurant,
    create_worker,
    delete_worker,
    get_all_workers,
    get_worker_by_id,
    remove_worker_from_restaurant,
)


class CreateWorkerRequest(BaseModel):
    email: EmailStr
    password: str


router = APIRouter(
    prefix="/worker/panel",
    tags=["admin panel workers"],
    dependencies=[Depends(role_required(UserRole.ADMIN))],
)


@router.get("/all")
@handle_request_errors
async def get_workers(db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    return JSONResponse(content=jsonable_encoder(get_all_workers(db_ref)), status_code=status.HTTP_200_OK)


@router.get("/{worker_id}")
@handle_request_errors
async def get_worker(worker_id: str, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    return JSONResponse(content=jsonable_encoder(get_worker_by_id(worker_id, db_ref)), status_code=status.HTTP_200_OK)


@router.post("/create")
@handle_request_errors
async def add_worker(
    worker_data: CreateWorkerRequest, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    return JSONResponse(
        content=jsonable_encoder(create_worker(worker_data.email, db_ref, worker_data.password)),
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/{worker_id}/assign/{restaurant_id}")
@handle_request_errors
async def assign_to_restaurant(
    worker_id: str, restaurant_id: str, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    return JSONResponse(
        content=jsonable_encoder(assign_worker_to_restaurant(worker_id, restaurant_id, db_ref)),
        status_code=status.HTTP_200_OK,
    )


@router.post("/{worker_id}/remove-assignment")
@handle_request_errors
async def remove_from_restaurant(worker_id: str, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    return JSONResponse(
        content=jsonable_encoder(remove_worker_from_restaurant(worker_id, db_ref)),
        status_code=status.HTTP_200_OK,
    )


@router.delete("/{worker_id}")
@handle_request_errors
async def remove_worker(worker_id: str, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    return JSONResponse(content=jsonable_encoder(delete_worker(worker_id, db_ref)), status_code=status.HTTP_200_OK)
