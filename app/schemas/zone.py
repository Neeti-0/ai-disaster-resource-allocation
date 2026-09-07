from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class DamageLevel(str, Enum):
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"

class ZoneCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    population: int = Field(default=0, ge=0)
    affected_population: int = Field(default=0, ge=0)
    children_percentage: float = Field(default=0.0, ge=0, le=100)
    elderly_percentage: float = Field(default=0.0, ge=0, le=100)
    disabled_percentage: float = Field(default=0.0, ge=0, le=100)
    medical_need: float = Field(default=0.0, ge=0, le=1)
    food_need: float = Field(default=0.0, ge=0, le=1)
    water_need: float = Field(default=0.0, ge=0, le=1)
    shelter_need: float = Field(default=0.0, ge=0, le=1)
    road_accessibility: float = Field(default=0.5, ge=0, le=1)
    damage_level: DamageLevel = Field(default=DamageLevel.MINIMAL)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ludhiana North",
                "latitude": 31.8854,
                "longitude": 75.7521,
                "population": 100000,
                "affected_population": 45000,
                "children_percentage": 25,
                "elderly_percentage": 15,
                "disabled_percentage": 5,
                "medical_need": 0.85,
                "food_need": 0.90,
                "water_need": 0.95,
                "shelter_need": 0.70,
                "road_accessibility": 0.6,
                "damage_level": "severe"
            }
        }

class ZoneRead(ZoneCreate):
    id: int
    priority_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
