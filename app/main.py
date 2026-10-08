from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
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


# 1件取得
@app.get("/spots/{spot_id}", response_model=SpotRead)
def get_spot(spot_id: int, db: Session = Depends(get_db)):
    spot = db.get(Spot, spot_id)
    if spot is None:
        raise HTTPException(status_code=404, detail="Spot not found")
    return spot


# 編集
@app.put("/spots/{spot_id}", response_model=SpotRead)
def update_spot(spot_id: int, spot_in:SpotCreate, db:Session = Depends(get_db)):
    spot = db.get(Spot, spot_id)
    if spot is None:
        raise HTTPException(status_code=404, detail="Spot not found")
    
    for key, value in spot_in.model_dump().items():
        setattr(spot, key, value)
    
    db.commit()
    db.refresh(spot)
    return spot
