from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class AllocationDetail(BaseModel):
    resource: str
    resource_id: int
    quantity: int
    destination_zone: str
    destination_zone_id: int
    priority_score: float
    estimated_arrival_minutes: float
    reason: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "resource": "ambulance",
                "resource_id": 1,
                "quantity": 3,
                "destination_zone": "Ludhiana North",
                "destination_zone_id": 1,
                "priority_score": 0.94,
                "estimated_arrival_minutes": 17,
                "reason": [
                    "High medical demand",
                    "Large affected population",
                    "Limited existing medical resources",
                    "High vulnerability"
                ]
            }
        }

class OptimizationRequest(BaseModel):
    disaster_id: int
    scenario_id: Optional[int] = None
    optimization_mode: str = Field(default="maximum_humanitarian_impact")

    class Config:
        json_schema_extra = {
            "example": {
                "disaster_id": 1,
                "scenario_id": 101,
                "optimization_mode": "maximum_humanitarian_impact"
            }
        }

class OptimizationResponse(BaseModel):
    scenario_id: int
    status: str
    total_resources_allocated: int
    estimated_response_time_minutes: float
    estimated_population_served: int
    unserved_population: int
    allocations: List[AllocationDetail]
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_id": 101,
                "status": "optimized",
                "total_resources_allocated": 47,
                "estimated_response_time_minutes": 38,
                "estimated_population_served": 18400,
                "unserved_population": 1200,
                "allocations": [],
                "timestamp": "2024-09-07T12:00:00Z"
            }
        }

class AllocationRead(BaseModel):
    id: int
    scenario_id: int
    resource_id: int
    zone_id: int
    quantity_allocated: int
    estimated_arrival_minutes: float
    priority_score: float
    created_at: datetime

    class Config:
        from_attributes = True
