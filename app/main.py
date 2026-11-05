from fastapi import FastAPI

from app.routers import routes, spots

app = FastAPI()

app.include_router(spots.router)
app.include_router(routes.router)
