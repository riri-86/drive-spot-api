from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

spots = []


class SpotCreate(BaseModel):
    name: str
    address: str
    category: str
    memo: str | None = None
    visited: bool = False


@app.get("/spots")
def list_spots():
    return spots


@app.post("/spots" , status_code=201)
def create_spot(spot: SpotCreate):
    new_spot = {"id": len(spots) + 1, **spot.model_dump()}
    spots.append(new_spot)
    return new_spot


