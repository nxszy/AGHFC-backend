from fastapi import FastAPI
from app.routers import restaurants
from config import settings
import firebase_admin

app = FastAPI()

app.include_router(restaurants.router)

firebase_admin.initialize_app() 

@app.get("/")
async def test():
    return {"Hello"}