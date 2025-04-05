from fastapi import FastAPI, Response

from app.core.middleware import AuthMiddleware
from app.routers import restaurants

app = FastAPI()

app.add_middleware(AuthMiddleware)

app.include_router(restaurants.router)


@app.get("/")
async def test() -> Response:
    return Response({"hello": "there"})
