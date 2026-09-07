from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class ResourceCategory(str, Enum):
    HUMAN = "human"
    EQUIPMENT = "equipment"
    SUPPLIES = "supplies"

class ResourceType(str, Enum):
    RESCUE_TEAM = "rescue_team"
    MEDICAL_TEAM = "medical_team"
    FIREFIGHTERS = "firefighters"
    VOLUNTEERS = "volunteers"
    ENGINEERS = "engineers"
    AMBULANCE = "ambulance"
    RESCUE_VEHICLE = "rescue_vehicle"
    BOAT = "boat"
    HELICOPTER = "helicopter"
    EXCAVATOR = "excavator"
    WATER_TANKER = "water_tanker"
    GENERATOR = "generator"
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

class ResourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    resource_type: ResourceType
    category: ResourceCategory
    quantity: int = Field(..., ge=1)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    owner: str = Field(default="Unknown")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ambulance Fleet A",
                "resource_type": "ambulance",
                "category": "equipment",
                "quantity": 5,
                "latitude": 31.8854,
                "longitude": 75.7521,
                "owner": "Red Cross"
            }
        }

class ResourceUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    available_quantity: Optional[int] = Field(None, ge=0)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    status: Optional[ResourceStatus] = None

class ResourceRead(ResourceCreate):
    id: int
    available_quantity: int
    status: ResourceStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
