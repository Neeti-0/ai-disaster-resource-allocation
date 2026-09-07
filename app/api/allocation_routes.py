from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.schemas.allocation import OptimizationRequest, OptimizationResponse, AllocationDetail
from app.services.optimization_engine import OptimizationEngine
from app.services.explanation_engine import ExplanationEngine

router = APIRouter(prefix="/api/allocations", tags=["allocations"])

optimization_engine = OptimizationEngine()
explanation_engine = ExplanationEngine()

@router.post("/optimize", response_model=OptimizationResponse)
def optimize_allocation(
    request: OptimizationRequest,
    db: Session = Depends(get_db)
):
    """Run optimization and return resource allocation."""
    result = optimization_engine.optimize_allocation(db, request.scenario_id or 1)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Optimization failed")
        )
    
    # Add explanations to allocations
    allocations_with_explanations = []
    for alloc in result.get("allocations", []):
        explanation = explanation_engine.explain_allocation(alloc)
        allocations_with_explanations.append(
            AllocationDetail(
                resource=alloc["resource_name"],
                resource_id=alloc["resource_id"],
                quantity=alloc["quantity"],
                destination_zone=alloc["zone_name"],
                destination_zone_id=alloc["zone_id"],
                priority_score=alloc["priority_score"],
                estimated_arrival_minutes=alloc["travel_time_minutes"],
                reason=explanation
            )
        )
    
    return OptimizationResponse(
        scenario_id=result["scenario_id"],
        status=result["status"],
        total_resources_allocated=result["total_resources_allocated"],
        estimated_response_time_minutes=result["estimated_response_time_minutes"],
        estimated_population_served=result["estimated_population_served"],
        unserved_population=result["unserved_population"],
        allocations=allocations_with_explanations,
        timestamp=datetime.utcnow()
    )
