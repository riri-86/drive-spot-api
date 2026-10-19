from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# スポットクラスの生成
class SpotCreate(BaseModel):
    name: str
    address: str
    category: str
    memo: str | None = None
    visited: bool = False
    rating: int | None = Field(default=None, ge=1, le=5)


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
    rating: int | None 