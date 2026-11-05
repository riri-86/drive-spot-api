from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Spot(Base):
    __tablename__ = "spots"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    category = Column(String, nullable=False)
    memo = Column(String, nullable=True)
    visited = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    rating = Column(Integer, nullable=True)


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    origin_lat = Column(Float,nullable=False)
    origin_lng = Column(Float,nullable=False)
    destination_lat = Column(Float,nullable=False)
    destination_lng = Column(Float,nullable=False)
    length_km = Column(Float,nullable=False)
    detour_ratio = Column(Float,nullable=False)
    curve_deg_per_km = Column(Float,nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    vias = relationship(
        "RouteVia",
        back_populates="route",
        order_by="RouteVia.position",
        cascade="all, delete-orphan",
    )


class RouteVia(Base):
    __tablename__ = "route_vias"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False, index=True)
    position = Column(Integer, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    route = relationship("Route", back_populates="vias")
