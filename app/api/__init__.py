from app.api.disaster_routes import router as disaster_router
from app.api.resource_routes import router as resource_router
from app.api.facility_routes import router as facility_router
from app.api.zone_routes import router as zone_router
from app.api.allocation_routes import router as allocation_router
from app.api.scenario_routes import router as scenario_router
from app.api.priority_routes import router as priority_router
from app.api.health_routes import router as health_router

__all__ = [
    "disaster_router",
    "resource_router",
    "facility_router",
    "zone_router",
    "allocation_router",
    "scenario_router",
    "priority_router",
    "health_router"
]
