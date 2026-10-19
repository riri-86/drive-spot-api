from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Spot
from app.schemas.spot import SpotCreate, SpotRead

app = FastAPI()


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


# 削除
@app.delete("/spots/{spot_id}", status_code=204)
def delete_spot(spot_id: int, db: Session = Depends(get_db)):
    spot = db.get(Spot, spot_id)
    if spot is None:
        raise HTTPException(status_code=404, detail="Spot not found")

    db.delete(spot)
    db.commit()

