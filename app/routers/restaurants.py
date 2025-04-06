from fastapi import APIRouter, Response

router = APIRouter(
    prefix="/restaurants",
    tags=["restaurants"],
)


@router.get("/")
async def fetch_restaurants() -> Response:
    return Response({"cute": "example"})
