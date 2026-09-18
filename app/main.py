from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

spots = []

# スポットクラスの生成
class SpotCreate(BaseModel):
    name: str
    address: str
    category: str
    memo: str | None = None
    visited: bool = False

# スポット一覧取得
@app.get("/spots")
def list_spots():
    return spots

# スポット登録
@app.post("/spots" , status_code=201)
def create_spot(spot: SpotCreate):
    new_spot = {"id": len(spots) + 1, **spot.model_dump()}
    spots.append(new_spot)
    return new_spot


# データベース
from sqlalchemy import create_engine
from sqlalchemy import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./spots.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread":False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
