import logging
from typing import Dict, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.allocation import Allocation
from app.models.resource import Resource
from app.models.zone import AffectedZone

logger = logging.getLogger(__name__)

class ExplanationEngine:
    """Generate human-readable explanations for allocations."""
    
    def explain_allocation(self, allocation: Dict) -> List[str]:
        """
        Generate reasons for an allocation.
        
        Args:
            allocation: Dict with allocation details
        
        Returns:
            List of human-readable reasons
        """
        reasons = []
        
        priority_score = allocation.get("priority_score", 0)
        demand = allocation.get("demand", 0)
        distance = allocation.get("distance", 0)
        travel_time = allocation.get("travel_time_minutes", 0)
        
        # Priority-based reasons
        if priority_score >= 0.85:
            reasons.append("Critical priority zone")
        elif priority_score >= 0.7:
            reasons.append("High priority zone")
        
        # Demand-based reasons
        if allocation.get("medical_need", 0) > 0.7:
            reasons.append("High medical demand")
        if allocation.get("food_need", 0) > 0.7:
            reasons.append("Critical food shortage")
        if allocation.get("water_need", 0) > 0.7:
            reasons.append("Critical water shortage")
        if allocation.get("shelter_need", 0) > 0.7:
            reasons.append("High shelter need")
        
        # Population-based reasons
        if allocation.get("affected_population", 0) > 10000:
            reasons.append("Large affected population")
        if allocation.get("vulnerability", 0) > 0.5:
            reasons.append("High vulnerable population (children/elderly/disabled)")
        
        # Resource constraints
        if allocation.get("limited_local_resources", False):
            reasons.append("Limited existing resources in zone")
        
        # Accessibility
        if allocation.get("road_accessibility", 1.0) < 0.5:
            reasons.append("Limited road access; must prioritize")
        elif distance > 50:
            reasons.append("Distance justified by resource scarcity")
        
        # Route quality
        if travel_time < 20:
            reasons.append("Fastest feasible route available")
        elif travel_time < 60:
            reasons.append("Good route accessibility")
        
        # If no specific reasons, add generic ones
        if not reasons:
            reasons.append("Needed to serve affected population")
            reasons.append("Optimal allocation considering constraints")
        
        return reasons
    
    def explain_changes(self, old_allocation: Dict, new_allocation: Dict, 
                       change_trigger: str) -> Dict:
        """
        Explain why allocation changed.
        
        Args:
            old_allocation: Previous allocation
            new_allocation: New allocation
            change_trigger: What caused the change
        
        Returns:
            Dict with explanation
        """
        changes = []
        
        # Find differences
        for zone_id in set(list(old_allocation.keys()) + list(new_allocation.keys())):
            old_qty = old_allocation.get(zone_id, {}).get("quantity", 0)
            new_qty = new_allocation.get(zone_id, {}).get("quantity", 0)
            
            if old_qty != new_qty:
                if new_qty > old_qty:
                    changes.append({
                        "zone_id": zone_id,
                        "change": "increased",
                        "old_quantity": old_qty,
                        "new_quantity": new_qty,
                        "reason": self._get_increase_reason(change_trigger)
                    })
                else:
                    changes.append({
                        "zone_id": zone_id,
                        "change": "decreased",
                        "old_quantity": old_qty,
                        "new_quantity": new_qty,
                        "reason": self._get_decrease_reason(change_trigger)
                    })
        
        return {
            "trigger": change_trigger,
            "timestamp": datetime.utcnow().isoformat(),
            "changes": changes
        }
    
    def _get_increase_reason(self, trigger: str) -> str:
        """Get reason for allocation increase."""
        reasons = {
            "road_blocked": "Route became unavailable; additional resources needed",
            "resource_added": "New resources available for allocation",
            "population_increase": "Population affected increased; more resources needed",
            "medical_increase": "Medical demand increased; more medical resources needed",
            "facility_closed": "Facility unavailable; alternative capacity needed"
        }
        return reasons.get(trigger, "Zone priority increased")
    
    def _get_decrease_reason(self, trigger: str) -> str:
        """Get reason for allocation decrease."""
        reasons = {
            "road_restored": "Better route now available; resources redirected",
            "resource_removed": "Resource no longer available; reallocation needed",
            "population_decrease": "Affected population decreased; fewer resources needed",
            "facility_opened": "Alternative facility available; reallocation possible"
        }
        return reasons.get(trigger, "Zone priority decreased")
