from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
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

class FacilityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    facility_type: FacilityType
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    capacity: int = Field(..., ge=1)
    medical_capacity: int = Field(default=0, ge=0)
    storage_capacity: int = Field(default=0, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Civil Hospital Ludhiana",
                "facility_type": "hospital",
                "latitude": 30.9010,
                "longitude": 75.8573,
                "capacity": 500,
                "medical_capacity": 200,
                "storage_capacity": 0
            }
        }

class FacilityRead(FacilityCreate):
    id: int
    current_occupancy: int
    remaining_capacity: int
    status: FacilityStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
