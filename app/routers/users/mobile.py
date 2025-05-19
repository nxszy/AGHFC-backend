from fastapi import APIRouter, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.models.user import DisplayedUser

from app.services.shared.request_handler import handle_request_errors

router = APIRouter(
    prefix="/users/mobile",
    tags=["mobile users endpoints"],
)


@handle_request_errors
@router.get("/me")
async def get_user_data(
        request: Request,
) -> Response:
    displayed_user = DisplayedUser(**request.state.user.model_dump())

    return JSONResponse(content=jsonable_encoder(displayed_user.model_dump()), status_code=status.HTTP_201_CREATED)
