from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum

class DamageLevel(str, Enum):
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"

class AffectedZone(Base):
    __tablename__ = "affected_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    population = Column(Integer, default=0)
    affected_population = Column(Integer, default=0)
    children_percentage = Column(Float, default=0.0)  # 0-100
    elderly_percentage = Column(Float, default=0.0)  # 0-100
    disabled_percentage = Column(Float, default=0.0)  # 0-100
    medical_need = Column(Float, default=0.0)  # 0-1
    food_need = Column(Float, default=0.0)  # 0-1
    water_need = Column(Float, default=0.0)  # 0-1
    shelter_need = Column(Float, default=0.0)  # 0-1
    road_accessibility = Column(Float, default=0.5)  # 0-1 (1 = fully accessible)
    damage_level = Column(SQLEnum(DamageLevel), default=DamageLevel.MINIMAL, index=True)
    priority_score = Column(Float, default=0.0)  # Calculated dynamically
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
