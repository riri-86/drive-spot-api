from datetime import datetime

from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Spot

app = FastAPI()


# スポットクラスの生成
class SpotCreate(BaseModel):
    name: str
    address: str
    category: str
    memo: str | None = None
    visited: bool = False


#スポットクラスの参照
class SpotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    category: str
    memo: str | None
    visited: bool
    created_at: datetime


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# スポット一覧取得
@app.get("/spots", response_model=list[SpotRead])
def list_spots(db: Session = Depends(get_db)):
    return db.scalars(select(Spot)).all()


# スポット登録
@app.post("/spots", response_model=SpotRead, status_code=201)
def create_spot(spot: SpotCreate, db: Session = Depends(get_db)):
    new_spot = Spot(**spot.model_dump())
    db.add(new_spot)
    db.commit()
    db.refresh(new_spot)
    return new_spot