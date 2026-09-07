from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Disaster Resource Allocation Backend"
    }
