from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.scenario import Scenario
from app.schemas.scenario import ScenarioCreate, ScenarioRead, ScenarioModify
from app.services.scenario_engine import ScenarioEngine
from typing import List

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])

scenario_engine = ScenarioEngine()

@router.post("/", response_model=ScenarioRead, status_code=status.HTTP_201_CREATED)
def create_scenario(scenario: ScenarioCreate, db: Session = Depends(get_db)):
    """Create a new scenario."""
    db_scenario = scenario_engine.create_scenario(
        db,
        scenario.disaster_id,
        scenario.name,
        scenario.description,
        scenario.scenario_data
    )
    return db_scenario

@router.get("/{scenario_id}", response_model=ScenarioRead)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Get a specific scenario."""
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )
    return scenario

@router.post("/{scenario_id}/simulate")
def simulate_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Run optimization for a scenario."""
    result = scenario_engine.simulate_scenario(db, scenario_id)
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message")
        )
    return result

@router.post("/{scenario_id}/modify")
def modify_scenario(
    scenario_id: int,
    modification: ScenarioModify,
    db: Session = Depends(get_db)
):
    """Modify scenario and recalculate allocation."""
    result = scenario_engine.modify_scenario(
        db,
        scenario_id,
        modification.change_type,
        modification.change_data
    )
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message")
        )
    return result

@router.get("/{scenario_id}/compare")
def compare_scenarios(
    scenario_id: int,
    other_scenario_id: int,
    db: Session = Depends(get_db)
):
    """Compare two scenarios."""
    result = scenario_engine.compare_scenarios(db, scenario_id, other_scenario_id)
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message")
        )
    return result
