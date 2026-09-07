from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.zone import AffectedZone
from app.schemas.zone import ZoneCreate, ZoneRead

router = APIRouter(prefix="/api/zones", tags=["zones"])

@router.post("/", response_model=ZoneRead, status_code=status.HTTP_201_CREATED)
def create_zone(zone: ZoneCreate, db: Session = Depends(get_db)):
    """Create a new affected zone."""
    db_zone = AffectedZone(**zone.dict())
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone

@router.get("/", response_model=List[ZoneRead])
def get_zones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all affected zones."""
    return db.query(AffectedZone).offset(skip).limit(limit).all()

@router.get("/{zone_id}", response_model=ZoneRead)
def get_zone(zone_id: int, db: Session = Depends(get_db)):
    """Get a specific zone by ID."""
    zone = db.query(AffectedZone).filter(AffectedZone.id == zone_id).first()
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found"
        )
    return zone
