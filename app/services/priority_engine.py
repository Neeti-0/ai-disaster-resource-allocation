import math
from typing import Dict, List
from app.core.config import get_settings
from sqlalchemy.orm import Session
from app.models.zone import AffectedZone

class PriorityEngine:
    """Calculate priority scores for affected zones."""
    
    def __init__(self):
        self.settings = get_settings()
        self.weights = self.settings.PRIORITY_WEIGHTS
    
    def calculate_priority_score(self, zone: AffectedZone) -> Dict:
        """
        Calculate the priority score for an affected zone.
        
        Returns:
            Dict with priority_score, priority_level, and factor breakdown
        """
        # Normalize all factors to 0-1
        population_factor = self._normalize_population(zone)
        medical_factor = zone.medical_need  # Already 0-1
        vulnerability_factor = self._calculate_vulnerability(zone)
        damage_factor = self._damage_to_factor(zone.damage_level)
        shortage_factor = self._calculate_shortage_factor(zone)
        accessibility_factor = zone.road_accessibility  # Already 0-1
        
        # Weighted sum
        priority_score = (
            self.weights["population"] * population_factor +
            self.weights["medical_need"] * medical_factor +
            self.weights["vulnerability"] * vulnerability_factor +
            self.weights["damage"] * damage_factor +
            self.weights["shortage"] * shortage_factor +
            self.weights["accessibility"] * (1 - accessibility_factor)  # Lower accessibility = higher priority
        )
        
        priority_level = self._score_to_level(priority_score)
        
        return {
            "zone_id": zone.id,
            "zone_name": zone.name,
            "priority_score": round(priority_score, 4),
            "priority_level": priority_level,
            "factors": {
                "population": round(population_factor, 3),
                "medical_need": round(medical_factor, 3),
                "vulnerability": round(vulnerability_factor, 3),
                "damage": round(damage_factor, 3),
                "shortage": round(shortage_factor, 3),
                "accessibility": round(accessibility_factor, 3)
            }
        }
    
    def _normalize_population(self, zone: AffectedZone) -> float:
        """Normalize affected population (0-1)."""
        if zone.population == 0:
            return 0.0
        ratio = zone.affected_population / max(zone.population, zone.affected_population)
        return min(ratio, 1.0)
    
    def _calculate_vulnerability(self, zone: AffectedZone) -> float:
        """Calculate vulnerability based on demographics."""
        children_weight = 0.35
        elderly_weight = 0.35
        disabled_weight = 0.30
        
        vulnerability = (
            children_weight * (zone.children_percentage / 100) +
            elderly_weight * (zone.elderly_percentage / 100) +
            disabled_weight * (zone.disabled_percentage / 100)
        )
        return min(vulnerability, 1.0)
    
    def _damage_to_factor(self, damage_level: str) -> float:
        """Convert damage level to factor (0-1)."""
        damage_map = {
            "minimal": 0.1,
            "moderate": 0.4,
            "severe": 0.75,
            "critical": 1.0
        }
        return damage_map.get(damage_level, 0.0)
    
    def _calculate_shortage_factor(self, zone: AffectedZone) -> float:
        """Calculate resource shortage factor."""
        # Combine multiple needs
        needs = [
            zone.food_need,
            zone.water_need,
            zone.medical_need,
            zone.shelter_need
        ]
        return min(sum(needs) / len(needs), 1.0) if needs else 0.0
    
    def _score_to_level(self, score: float) -> str:
        """Convert score to priority level."""
        if score >= 0.85:
            return "CRITICAL"
        elif score >= 0.7:
            return "HIGH"
        elif score >= 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def calculate_all_priorities(self, db: Session) -> List[Dict]:
        """Calculate priorities for all zones."""
        zones = db.query(AffectedZone).all()
        priorities = []
        for zone in zones:
            priority = self.calculate_priority_score(zone)
            priorities.append(priority)
            # Update zone with new priority score
            zone.priority_score = priority["priority_score"]
        db.commit()
        return sorted(priorities, key=lambda x: x["priority_score"], reverse=True)
