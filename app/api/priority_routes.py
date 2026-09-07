from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.priority_engine import PriorityEngine

router = APIRouter(prefix="/api/priorities", tags=["priorities"])

priority_engine = PriorityEngine()

@router.get("/")
def get_all_priorities(db: Session = Depends(get_db)):
    """Get priority scores for all zones."""
    priorities = priority_engine.calculate_all_priorities(db)
    return {"priorities": priorities}

@router.get("/{zone_id}")
def get_zone_priority(zone_id: int, db: Session = Depends(get_db)):
    """Get priority score for a specific zone."""
    from app.models.zone import AffectedZone
    zone = db.query(AffectedZone).filter(AffectedZone.id == zone_id).first()
    if not zone:
        return {"error": "Zone not found"}
    return priority_engine.calculate_priority_score(zone)
