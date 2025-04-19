from fastapi import FastAPI

from app.core.middleware import AuthMiddleware
from app.routers.orders import mobile as orders_mobile
from app.routers.restaurants import mobile as restaurant_mobile
from app.routers.restaurants import panel as panel_mobile

app = FastAPI()

app.add_middleware(AuthMiddleware)

app.include_router(restaurant_mobile.router)
app.include_router(panel_mobile.router)

app.include_router(orders_mobile.router)
