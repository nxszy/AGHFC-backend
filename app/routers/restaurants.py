from fastapi import APIRouter

router = APIRouter(
    prefix="/restaurants",
    tags=["restaurants"],
)

@router.get("/")
async def fetch_restaurants():
    return {"cute":"example"}