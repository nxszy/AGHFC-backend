from typing import Any

from fastapi import HTTPException, Request, status


def role_required(expected_role: str) -> Any:
    async def dependency(request: Request) -> None:
        user = request.state.user

        if not user or user.role != expected_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )

    return dependency
