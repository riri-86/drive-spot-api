from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from database import Base


class Spot(Base):
    __tablename__ = "spots"

    id = Column(Integer, primeary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    category = Column(String, nullable=False)
    memo = Column(String, nullable=True)
    visited = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
