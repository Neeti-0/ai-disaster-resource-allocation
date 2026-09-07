from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.facility import Facility
from app.schemas.facility import FacilityCreate, FacilityRead

router = APIRouter(prefix="/api/facilities", tags=["facilities"])

@router.post("/", response_model=FacilityRead, status_code=status.HTTP_201_CREATED)
def create_facility(facility: FacilityCreate, db: Session = Depends(get_db)):
    """Create a new facility."""
    if facility.capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Facility capacity must be positive"
        )
    db_facility = Facility(**facility.dict())
    db.add(db_facility)
    db.commit()
    db.refresh(db_facility)
    return db_facility

@router.get("/", response_model=List[FacilityRead])
def get_facilities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all facilities."""
    return db.query(Facility).offset(skip).limit(limit).all()

@router.get("/{facility_id}", response_model=FacilityRead)
def get_facility(facility_id: int, db: Session = Depends(get_db)):
    """Get a specific facility by ID."""
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
    return facility
