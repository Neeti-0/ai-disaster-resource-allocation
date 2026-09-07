from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.disaster import Disaster
from app.schemas.disaster import DisasterCreate, DisasterRead

router = APIRouter(prefix="/api/disasters", tags=["disasters"])

@router.post("/", response_model=DisasterRead, status_code=status.HTTP_201_CREATED)
def create_disaster(disaster: DisasterCreate, db: Session = Depends(get_db)):
    """Create a new disaster."""
    db_disaster = Disaster(**disaster.dict())
    db.add(db_disaster)
    db.commit()
    db.refresh(db_disaster)
    return db_disaster

@router.get("/", response_model=List[DisasterRead])
def get_disasters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all disasters."""
    return db.query(Disaster).offset(skip).limit(limit).all()

@router.get("/{disaster_id}", response_model=DisasterRead)
def get_disaster(disaster_id: int, db: Session = Depends(get_db)):
    """Get a specific disaster by ID."""
    disaster = db.query(Disaster).filter(Disaster.id == disaster_id).first()
    if not disaster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disaster not found"
        )
    return disaster

@router.delete("/{disaster_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disaster(disaster_id: int, db: Session = Depends(get_db)):
    """Delete a disaster."""
    disaster = db.query(Disaster).filter(Disaster.id == disaster_id).first()
    if not disaster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disaster not found"
        )
    db.delete(disaster)
    db.commit()
    return None
