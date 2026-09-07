from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

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

class DisasterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    disaster_type: DisasterType
    severity: int = Field(..., ge=1, le=10)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    affected_population: int = Field(default=0, ge=0)
    affected_area: float = Field(default=0.0, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Punjab Flood 2024",
                "disaster_type": "flood",
                "severity": 8,
                "latitude": 31.8854,
                "longitude": 75.7521,
                "affected_population": 50000,
                "affected_area": 250.5
            }
        }

class DisasterRead(DisasterCreate):
    id: int
    status: DisasterStatus
    start_time: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
