from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.resource import Resource
from app.schemas.resource import ResourceCreate, ResourceRead, ResourceUpdate

router = APIRouter(prefix="/api/resources", tags=["resources"])

@router.post("/", response_model=ResourceRead, status_code=status.HTTP_201_CREATED)
def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    """Create a new resource."""
    if resource.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource quantity must be positive"
        )
    db_resource = Resource(**resource.dict())
    db_resource.available_quantity = resource.quantity
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

@router.get("/", response_model=List[ResourceRead])
def get_resources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all resources."""
    return db.query(Resource).offset(skip).limit(limit).all()

@router.get("/{resource_id}", response_model=ResourceRead)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    """Get a specific resource by ID."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    return resource

@router.patch("/{resource_id}", response_model=ResourceRead)
def update_resource(
    resource_id: int,
    update: ResourceUpdate,
    db: Session = Depends(get_db)
):
    """Update a resource."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)
    
    db.commit()
    db.refresh(resource)
    return resource
