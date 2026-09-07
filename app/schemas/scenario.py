from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ScenarioCreate(BaseModel):
    disaster_id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scenario_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "disaster_id": 1,
                "name": "Punjab Flood - Main Scenario",
                "description": "Base scenario for Punjab flood with all roads open",
                "scenario_data": {}
            }
        }

class ScenarioModify(BaseModel):
    change_type: str  # road_blocked, resource_added, population_increase, etc.
    change_data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "change_type": "road_blocked",
                "change_data": {
                    "road_id": "R102",
                    "from_node": "A",
                    "to_node": "B"
                }
            }
        }

class ComparisonResult(BaseModel):
    parameter: str
    baseline_value: Any
    modified_value: Any
    difference: str
    percentage_change: Optional[float] = None

class ScenarioComparison(BaseModel):
    baseline_scenario_id: int
    modified_scenario_id: int
    differences: List[ComparisonResult]
    reallocation_summary: Dict[str, Any]

class ScenarioRead(ScenarioCreate):
    id: int
    total_resources_allocated: int
    estimated_response_time_minutes: float
    estimated_population_served: int
    unserved_population: int
    optimization_result: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
