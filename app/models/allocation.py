from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Allocation(Base):
    __tablename__ = "allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), index=True)
    zone_id = Column(Integer, ForeignKey("affected_zones.id"), index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=True)
    quantity_allocated = Column(Integer)
    estimated_arrival_minutes = Column(Float)
    priority_score = Column(Float)
    explanation = Column(String)  # JSON string with explanation
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
