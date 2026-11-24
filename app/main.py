from fastapi import FastAPI

from app.routers import pages, routes, spots

app = FastAPI()

app.include_router(pages.router)
app.include_router(spots.router)
app.include_router(routes.router)
