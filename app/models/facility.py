from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum

class FacilityType(str, Enum):
    HOSPITAL = "hospital"
    SHELTER = "shelter"
    WAREHOUSE = "warehouse"
    RELIEF_CAMP = "relief_camp"
    FIRE_STATION = "fire_station"
    POLICE_STATION = "police_station"

class FacilityStatus(str, Enum):
    OPERATIONAL = "operational"
    PARTIAL = "partial"
    DAMAGED = "damaged"
    CLOSED = "closed"

class Facility(Base):
    __tablename__ = "facilities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    facility_type = Column(SQLEnum(FacilityType), index=True)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    capacity = Column(Integer)  # Total capacity
    current_occupancy = Column(Integer, default=0)
    medical_capacity = Column(Integer, default=0)  # For hospitals
    storage_capacity = Column(Integer, default=0)  # For warehouses
    status = Column(SQLEnum(FacilityStatus), default=FacilityStatus.OPERATIONAL, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    @property
    def remaining_capacity(self):
        """Calculate remaining capacity."""
        return max(0, self.capacity - self.current_occupancy)
