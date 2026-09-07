import logging
import json
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models.scenario import Scenario, ScenarioChange
from app.models.road import Road, RoadStatus
from app.models.resource import Resource
from app.models.zone import AffectedZone
from app.services.optimization_engine import OptimizationEngine
from app.services.routing_engine import RoutingEngine

logger = logging.getLogger(__name__)

class ScenarioEngine:
    """Manage disaster scenarios and modifications."""
    
    def __init__(self):
        self.optimization_engine = OptimizationEngine()
        self.routing_engine = RoutingEngine()
    
    def create_scenario(self, db: Session, disaster_id: int, name: str,
                       description: str = "", scenario_data: Dict = None) -> Scenario:
        """
        Create a new scenario.
        """
        if scenario_data is None:
            scenario_data = {}
        
        scenario = Scenario(
            disaster_id=disaster_id,
            name=name,
            description=description,
            scenario_data=json.dumps(scenario_data)
        )
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        return scenario
    
    def simulate_scenario(self, db: Session, scenario_id: int) -> Dict:
        """
        Run optimization for a scenario.
        """
        scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return {"status": "error", "message": "Scenario not found"}
        
        result = self.optimization_engine.optimize_allocation(db, scenario_id)
        
        if result["status"] == "optimized":
            scenario.total_resources_allocated = result["total_resources_allocated"]
            scenario.estimated_response_time_minutes = result[
                "estimated_response_time_minutes"
            ]
            scenario.estimated_population_served = result[
                "estimated_population_served"
            ]
            scenario.unserved_population = result["unserved_population"]
            scenario.optimization_result = json.dumps(result)
            db.commit()
        
        return result
    
    def modify_scenario(self, db: Session, scenario_id: int, change_type: str,
                       change_data: Dict) -> Dict:
        """
        Modify scenario and recalculate allocation.
        
        Args:
            scenario_id: ID of scenario to modify
            change_type: Type of change (road_blocked, resource_added, etc.)
            change_data: Details of the change
        
        Returns:
            Dict with changes and new allocation
        """
        scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return {"status": "error", "message": "Scenario not found"}
        
        # Get previous allocation
        previous_result = json.loads(scenario.optimization_result) if scenario.optimization_result else {}
        
        # Apply change
        self._apply_change(db, change_type, change_data)
        
        # Recalculate
        new_result = self.simulation_scenario(db, scenario_id)
        
        # Record change
        change_record = ScenarioChange(
            scenario_id=scenario_id,
            change_type=change_type,
            change_data=json.dumps(change_data),
            previous_allocation=json.dumps(previous_result),
            new_allocation=json.dumps(new_result)
        )
        db.add(change_record)
        db.commit()
        
        return {
            "trigger": change_type,
            "change_data": change_data,
            "previous_allocation": previous_result,
            "new_allocation": new_result,
            "differences": self._compare_allocations(previous_result, new_result)
        }
    
    def _apply_change(self, db: Session, change_type: str, change_data: Dict):
        """
        Apply scenario modifications to database.
        """
        if change_type == "road_blocked":
            self.routing_engine.block_road(change_data.get("road_id"), db)
        
        elif change_type == "road_restored":
            self.routing_engine.restore_road(change_data.get("road_id"), db)
        
        elif change_type == "resource_added":
            # Add new resource (would require full resource creation)
            pass
        
        elif change_type == "resource_removed":
            resource_id = change_data.get("resource_id")
            resource = db.query(Resource).filter(Resource.id == resource_id).first()
            if resource:
                resource.available_quantity = 0
                db.commit()
        
        elif change_type == "population_increase":
            zone_id = change_data.get("zone_id")
            increase_percent = change_data.get("increase_percent", 0)
            zone = db.query(AffectedZone).filter(AffectedZone.id == zone_id).first()
            if zone:
                zone.affected_population = int(
                    zone.affected_population * (1 + increase_percent / 100)
                )
                db.commit()
        
        elif change_type == "medical_increase":
            zone_id = change_data.get("zone_id")
            zone = db.query(AffectedZone).filter(AffectedZone.id == zone_id).first()
            if zone:
                zone.medical_need = min(1.0, zone.medical_need + 0.2)
                db.commit()
    
    def _compare_allocations(self, old: Dict, new: Dict) -> Dict:
        """
        Compare two allocations and return differences.
        """
        differences = {
            "response_time_change": round(
                (new.get("estimated_response_time_minutes", 0) - 
                 old.get("estimated_response_time_minutes", 0)),
                2
            ),
            "population_served_change": (
                new.get("estimated_population_served", 0) - 
                old.get("estimated_population_served", 0)
            ),
            "unserved_change": (
                new.get("unserved_population", 0) - 
                old.get("unserved_population", 0)
            )
        }
        return differences
    
    def compare_scenarios(self, db: Session, scenario1_id: int, 
                         scenario2_id: int) -> Dict:
        """
        Compare two scenarios.
        """
        s1 = db.query(Scenario).filter(Scenario.id == scenario1_id).first()
        s2 = db.query(Scenario).filter(Scenario.id == scenario2_id).first()
        
        if not s1 or not s2:
            return {"status": "error", "message": "One or both scenarios not found"}
        
        r1 = json.loads(s1.optimization_result) if s1.optimization_result else {}
        r2 = json.loads(s2.optimization_result) if s2.optimization_result else {}
        
        return {
            "scenario_1": {
                "id": s1.id,
                "name": s1.name,
                "metrics": {
                    "resources_allocated": r1.get("total_resources_allocated"),
                    "response_time_minutes": r1.get("estimated_response_time_minutes"),
                    "population_served": r1.get("estimated_population_served"),
                    "unserved_population": r1.get("unserved_population")
                }
            },
            "scenario_2": {
                "id": s2.id,
                "name": s2.name,
                "metrics": {
                    "resources_allocated": r2.get("total_resources_allocated"),
                    "response_time_minutes": r2.get("estimated_response_time_minutes"),
                    "population_served": r2.get("estimated_population_served"),
                    "unserved_population": r2.get("unserved_population")
                }
            },
            "differences": self._compare_allocations(r1, r2)
        }
