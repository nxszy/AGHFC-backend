from fastapi import APIRouter, Depends, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import firestore  # type: ignore
from pydantic import BaseModel

from app.core.database import get_database_ref
from app.models.user import UserRole
from app.services.shared.request_handler import handle_request_errors
from app.services.shared.user_role_handler import role_required
from app.services.special_offers.panel import (
    add_special_offer_to_restaurant, create_special_offer,
    delete_special_offer, get_all_special_offers, get_special_offer_by_id,
    remove_special_offer_from_restaurant, update_special_offer)


class CreateSpecialOfferRequest(BaseModel):
    dish_id: str
    special_price: float


class UpdateSpecialOfferRequest(BaseModel):
    special_price: float


router = APIRouter(
    prefix="/special_offer/panel",
    tags=["admin panel special offers"],
    dependencies=[Depends(role_required(UserRole.ADMIN))],
)


@router.get("/all")
@handle_request_errors
async def get_offers(db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    return JSONResponse(content=jsonable_encoder(get_all_special_offers(db_ref)), status_code=status.HTTP_200_OK)


@router.get("/{offer_id}")
@handle_request_errors
async def get_offer(offer_id: str, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    return JSONResponse(
        content=jsonable_encoder(get_special_offer_by_id(offer_id, db_ref)), status_code=status.HTTP_200_OK
    )


@router.post("/create")
@handle_request_errors
async def create_offer(
    offer_data: CreateSpecialOfferRequest, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    return JSONResponse(
        content=jsonable_encoder(create_special_offer(offer_data.dish_id, offer_data.special_price, db_ref)),
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/{offer_id}")
@handle_request_errors
async def update_offer(
    offer_id: str, offer_data: UpdateSpecialOfferRequest, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    return JSONResponse(
        content=jsonable_encoder(update_special_offer(offer_id, offer_data.special_price, db_ref)),
        status_code=status.HTTP_200_OK,
    )


@router.delete("/{offer_id}")
@handle_request_errors
async def delete_offer(offer_id: str, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    return JSONResponse(
        content=jsonable_encoder(delete_special_offer(offer_id, db_ref)), status_code=status.HTTP_200_OK
    )


@router.post("/restaurant/{restaurant_id}/offer/{offer_id}")
@handle_request_errors
async def add_offer_to_restaurant(
    restaurant_id: str, offer_id: str, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    return JSONResponse(
        content=jsonable_encoder(add_special_offer_to_restaurant(restaurant_id, offer_id, db_ref)),
        status_code=status.HTTP_200_OK,
    )


@router.delete("/restaurant/{restaurant_id}/offer/{offer_id}")
@handle_request_errors
async def remove_offer_from_restaurant(
    restaurant_id: str, offer_id: str, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    return JSONResponse(
        content=jsonable_encoder(remove_special_offer_from_restaurant(restaurant_id, offer_id, db_ref)),
        status_code=status.HTTP_200_OK,
    )
