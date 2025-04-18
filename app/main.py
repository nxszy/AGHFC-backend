from fastapi import FastAPI

from app.core.middleware import AuthMiddleware
from app.routers.restaurants import mobile, panel

app = FastAPI()

app.add_middleware(AuthMiddleware)

app.include_router(mobile.router)
app.include_router(panel.router)
