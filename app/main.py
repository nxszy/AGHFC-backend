from fastapi import Depends, FastAPI
from fastapi.security import HTTPBearer

from app.core.middleware import AuthMiddleware
from app.routers.orders import mobile as orders_mobile
from app.routers.orders import panel as orders_panel
from app.routers.orders import worker_panel as orders_worker_panel
from app.routers.restaurants import mobile as restaurant_mobile
from app.routers.restaurants import panel as panel_mobile
from app.routers.special_offers import mobile as special_offers_mobile

security_scheme = HTTPBearer()

app = FastAPI(
    dependencies=[Depends(security_scheme)],
)

app.add_middleware(AuthMiddleware)

app.include_router(restaurant_mobile.router)
app.include_router(panel_mobile.router)

app.include_router(orders_mobile.router)
app.include_router(orders_panel.router)
app.include_router(orders_worker_panel.router)
app.include_router(special_offers_mobile.router)
