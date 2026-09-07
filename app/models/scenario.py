from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Scenario(Base):
    __tablename__ = "scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    disaster_id = Column(Integer, ForeignKey("disasters.id"), index=True)
    name = Column(String, index=True)
    description = Column(String)
    scenario_data = Column(String)  # JSON string with scenario parameters
    optimization_result = Column(String)  # JSON string with result
    total_resources_allocated = Column(Integer, default=0)
    estimated_response_time_minutes = Column(Float, default=0.0)
    estimated_population_served = Column(Integer, default=0)
    unserved_population = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ScenarioChange(Base):
    __tablename__ = "scenario_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), index=True)
    change_type = Column(String)  # road_blocked, resource_added, etc.
    change_data = Column(String)  # JSON string with change details
    previous_allocation = Column(String)  # JSON
    new_allocation = Column(String)  # JSON
    created_at = Column(DateTime, server_default=func.now())
