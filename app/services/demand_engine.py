from typing import Dict, List
from app.core.config import get_settings
from sqlalchemy.orm import Session
from app.models.zone import AffectedZone

class DemandEngine:
    """Estimate resource demands for affected zones."""
    
    def __init__(self):
        self.settings = get_settings()
    
    def estimate_zone_demand(self, zone: AffectedZone) -> Dict[str, float]:
        """
        Estimate resource demands for a zone.
        
        Returns:
            Dict with resource type and estimated quantity
        """
        pop = zone.affected_population
        
        demand = {
            "water_litre": pop * self.settings.WATER_PER_PERSON_LITERS * zone.water_need,
            "food_packet": pop * self.settings.FOOD_PER_PERSON_PACKETS * zone.food_need,
            "medicine": (pop / 100) * self.settings.MEDICINE_PER_100_PEOPLE * zone.medical_need,
            "blanket": pop * self.settings.BLANKET_PER_PERSON * zone.shelter_need,
            "tent": pop * self.settings.TENT_PER_PERSON * zone.shelter_need,
            "ambulance": max(1, int(pop * 0.001)) if zone.medical_need > 0.5 else 0,
            "rescue_team": max(1, int(pop * 0.0001)),
            "generator": max(1, int(pop / 5000)) if zone.shelter_need > 0.5 else 0,
        }
        
        return {k: round(v, 2) for k, v in demand.items()}
    
    def estimate_all_demands(self, db: Session) -> Dict[int, Dict[str, float]]:
        """
        Estimate demands for all zones.
        
        Returns:
            Dict mapping zone_id to demands
        """
        zones = db.query(AffectedZone).all()
        all_demands = {}
        for zone in zones:
            all_demands[zone.id] = self.estimate_zone_demand(zone)
        return all_demands
    
    def aggregate_demands(self, zone_demands: Dict[int, Dict[str, float]]) -> Dict[str, float]:
        """
        Aggregate demands across all zones.
        
        Returns:
            Total demand per resource type
        """
        aggregated = {}
        for zone_id, demands in zone_demands.items():
            for resource_type, quantity in demands.items():
                aggregated[resource_type] = aggregated.get(resource_type, 0) + quantity
        return aggregated
