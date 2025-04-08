from fastapi import FastAPI, Response

from app.config import settings
from app.core.middleware import AuthMiddleware
from app.routers.restaurants import mobile, panel

app = FastAPI()

app.add_middleware(AuthMiddleware)

app.include_router(mobile.router)


@app.get("/")
async def test() -> Response:
    return Response({"hello": "there"})
