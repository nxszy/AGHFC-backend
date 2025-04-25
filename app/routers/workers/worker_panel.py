from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from firebase_admin import firestore
from pydantic import BaseModel, Field

from app.core.database import get_database_ref
from app.models.user import UserRole
from app.services.shared.request_handler import handle_request_errors
from app.services.shared.user_role_handler import role_required
from app.services.workers.panel import change_worker_password


class ChangePasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=4, description="New password for the worker")


router = APIRouter(
    prefix="/worker", tags=["worker self-service"], dependencies=[Depends(role_required(UserRole.WORKER))]
)


@router.post("/change-password")
@handle_request_errors
async def worker_change_password(
    password_data: ChangePasswordRequest, request: Request, db_ref: firestore.Client = Depends(get_database_ref)
) -> Response:
    result = change_worker_password(request.state.user.id, password_data.new_password, db_ref)

    return JSONResponse(content=jsonable_encoder(result), status_code=status.HTTP_200_OK)
