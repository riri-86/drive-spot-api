from fastapi import FastAPI

from app.routers import spots

app = FastAPI()

app.include_router(spots.router)
