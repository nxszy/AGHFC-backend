import logging
from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException, status
from firebase_admin import exceptions  # type: ignore

logger = logging.getLogger(__name__)


def handle_request_errors(func: Callable) -> Callable:
    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)

        except exceptions.FirebaseError as e:
            logger.error(f"Firebase error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to connect to Firestore database"
            )

        except ValueError as e:
            logger.error(f"Data conversion error: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error processing data from Firestore")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
            )

    return async_wrapper
