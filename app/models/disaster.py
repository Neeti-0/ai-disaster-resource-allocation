from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum
from datetime import datetime

class DisasterType(str, Enum):
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    CYCLONE = "cyclone"
    LANDSLIDE = "landslide"
    WILDFIRE = "wildfire"
    INDUSTRIAL_ACCIDENT = "industrial_accident"
    HEATWAVE = "heatwave"
    OTHER = "other"

class DisasterStatus(str, Enum):
    ACTIVE = "active"
    ONGOING = "ongoing"
    CONTROLLED = "controlled"
    RESOLVED = "resolved"

class Disaster(Base):
    __tablename__ = "disasters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    disaster_type = Column(SQLEnum(DisasterType), index=True)
    severity = Column(Integer)  # 1-10
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    affected_population = Column(Integer, default=0)
    affected_area = Column(Float, default=0.0)  # in km²
    status = Column(SQLEnum(DisasterStatus), default=DisasterStatus.ACTIVE, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
