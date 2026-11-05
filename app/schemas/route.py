from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# 経由地点(受け取る形)
class ViaCreate(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


# ルートの登録
class RouteCreate(BaseModel):
    name: str
    origin_lat: float = Field(ge=-90, le=90)
    origin_lng: float = Field(ge=-180, le=180)
    destination_lat: float = Field(ge=-180, le=180)
    destination_lng: float = Field(ge=-180, le=180)
    vias: list[ViaCreate] = Field(default_factory=list, max_length=10)


# 経由地点(返す形)
class ViaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position: int
    lat: float
    lng: float


# ルートの参照
class RouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    origin_lat: float
    origin_lng: float
    destination_lat: float
    destination_lng: float
    vias: list[ViaRead]
    length_km: float
    detour_ratio: float
    curve_deg_per_km: float
    created_at: datetime
