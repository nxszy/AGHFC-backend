from fastapi import FastAPI
from app.routers import restaurants
from app.core.middleware import AuthMiddleware

app = FastAPI()

app.add_middleware(AuthMiddleware)

app.include_router(restaurants.router)

@app.get("/")
async def test():
    return {"Hello"}