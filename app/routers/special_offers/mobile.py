from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import firestore  # type: ignore

from app.core.database import get_database_ref
from app.services.shared.request_handler import handle_request_errors
from app.services.special_offers.mobile import (
    generate_special_offer_for_user,
    get_restaurant_special_offers,
    get_user_special_offers,
)

router = APIRouter(
    prefix="/special_offer/mobile",
    tags=["mobile special offers"],
)


@router.get("/restaurant/{restaurant_id}")
@handle_request_errors
async def get_restaurant_offers(restaurant_id: str, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    return JSONResponse(
        content=jsonable_encoder(get_restaurant_special_offers(restaurant_id, db_ref)), status_code=status.HTTP_200_OK
    )


@router.get("/user")
@handle_request_errors
async def get_user_offers(request: Request, db_ref: firestore.Client = Depends(get_database_ref)) -> Response:
    return JSONResponse(
        content=jsonable_encoder(get_user_special_offers(request.state.user, db_ref)), status_code=status.HTTP_200_OK
    )


@router.patch("/generate")
@handle_request_errors
async def generate_offer(
    restaurant_id: str, request: Request, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    return JSONResponse(
        content=jsonable_encoder(generate_special_offer_for_user(request.state.user, restaurant_id, db_ref)),
        status_code=status.HTTP_200_OK,
    )
