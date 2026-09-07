from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum

class RoadStatus(str, Enum):
    OPEN = "open"
    BLOCKED = "blocked"
    DAMAGED = "damaged"
    RESTRICTED = "restricted"

class Road(Base):
    __tablename__ = "roads"
    
    id = Column(Integer, primary_key=True, index=True)
    road_id = Column(String, unique=True, index=True)
    from_node = Column(String, index=True)
    to_node = Column(String, index=True)
    from_latitude = Column(Float)
    from_longitude = Column(Float)
    to_latitude = Column(Float)
    to_longitude = Column(Float)
    distance = Column(Float)  # in km
    travel_time = Column(Float)  # in minutes
    status = Column(SQLEnum(RoadStatus), default=RoadStatus.OPEN, index=True)
    capacity = Column(Integer, default=100)  # Vehicle capacity
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
