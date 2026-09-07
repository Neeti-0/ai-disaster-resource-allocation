from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from enum import Enum
from datetime import datetime
from sqlalchemy import DateTime

class ResourceCategory(str, Enum):
    HUMAN = "human"
    EQUIPMENT = "equipment"
    SUPPLIES = "supplies"

class ResourceType(str, Enum):
    # Human resources
    RESCUE_TEAM = "rescue_team"
    MEDICAL_TEAM = "medical_team"
    FIREFIGHTERS = "firefighters"
    VOLUNTEERS = "volunteers"
    ENGINEERS = "engineers"
    # Equipment
    AMBULANCE = "ambulance"
    RESCUE_VEHICLE = "rescue_vehicle"
    BOAT = "boat"
    HELICOPTER = "helicopter"
    EXCAVATOR = "excavator"
    WATER_TANKER = "water_tanker"
    GENERATOR = "generator"
    # Supplies
    FOOD_PACKET = "food_packet"
    WATER_LITRE = "water_litre"
    MEDICINE = "medicine"
    BLANKET = "blanket"
    TENT = "tent"
    OXYGEN_CYLINDER = "oxygen_cylinder"

class ResourceStatus(str, Enum):
    AVAILABLE = "available"
    IN_TRANSIT = "in_transit"
    DEPLOYED = "deployed"
    DAMAGED = "damaged"
    UNAVAILABLE = "unavailable"

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    resource_type = Column(SQLEnum(ResourceType), index=True)
    category = Column(SQLEnum(ResourceCategory), index=True)
    quantity = Column(Integer)  # Total quantity
    available_quantity = Column(Integer)  # Currently available
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    owner = Column(String)  # NGO, Government, etc.
    status = Column(SQLEnum(ResourceStatus), default=ResourceStatus.AVAILABLE, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.available_quantity is None:
            self.available_quantity = self.quantity
