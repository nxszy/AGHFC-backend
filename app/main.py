from fastapi import Depends, FastAPI
from fastapi.security import HTTPBearer

from app.core.middleware import AuthMiddleware
from app.routers.dishes import mobile as dishes_mobile
from app.routers.dishes import panel as dishes_panel
from app.routers.orders import mobile as orders_mobile
from app.routers.orders import panel as orders_panel
from app.routers.orders import worker_panel as orders_worker_panel
from app.routers.restaurant_dishes import panel as restaurant_dishes_panel
from app.routers.restaurants import mobile as restaurant_mobile
from app.routers.restaurants import panel as panel_mobile
from app.routers.special_offers import mobile as special_offers_mobile
from app.routers.special_offers import panel as special_offers_panel
from app.routers.users import mobile as users_mobile
from app.routers.workers import panel as workers_panel
from app.routers.workers import worker_panel as worker_panel
from app.routers.opinions import mobile as opinions_mobile
from fastapi.middleware.cors import CORSMiddleware
security_scheme = HTTPBearer()

app = FastAPI(
    dependencies=[Depends(security_scheme)],
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

app.include_router(restaurant_mobile.router)
app.include_router(panel_mobile.router)

app.include_router(orders_mobile.router)
app.include_router(orders_panel.router)
app.include_router(orders_worker_panel.router)
app.include_router(special_offers_mobile.router)
app.include_router(special_offers_panel.router)
app.include_router(workers_panel.router)
app.include_router(worker_panel.router)
app.include_router(dishes_mobile.router)
app.include_router(dishes_panel.router)
app.include_router(restaurant_dishes_panel.router)
app.include_router(users_mobile.router)
app.include_router(opinions_mobile.router)
