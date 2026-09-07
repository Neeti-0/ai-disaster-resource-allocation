import logging
from typing import Dict, List, Tuple
from ortools.linear_solver import pywraplp
from sqlalchemy.orm import Session
from app.models.resource import Resource
from app.models.zone import AffectedZone
from app.models.facility import Facility
from app.services.priority_engine import PriorityEngine
from app.services.demand_engine import DemandEngine
from app.services.routing_engine import RoutingEngine

logger = logging.getLogger(__name__)

class OptimizationEngine:
    """Constraint-based resource allocation using OR-Tools."""
    
    def __init__(self):
        self.priority_engine = PriorityEngine()
        self.demand_engine = DemandEngine()
        self.routing_engine = RoutingEngine()
    
    def optimize_allocation(self, db: Session, scenario_id: int) -> Dict:
        """
        Optimize resource allocation across zones.
        
        Returns:
            Dict with allocation results and metrics
        """
        try:
            # Fetch all data
            zones = db.query(AffectedZone).all()
            resources = db.query(Resource).filter(
                Resource.available_quantity > 0
            ).all()
            facilities = db.query(Facility).all()
            
            if not zones or not resources:
                return {
                    "status": "error",
                    "message": "No zones or resources available"
                }
            
            # Calculate priorities
            priorities = {}
            for zone in zones:
                priority = self.priority_engine.calculate_priority_score(zone)
                priorities[zone.id] = priority["priority_score"]
            
            # Estimate demands
            zone_demands = self.demand_engine.estimate_all_demands(db)
            
            # Build routing graph
            self.routing_engine.build_graph(db)
            
            # Create solver
            solver = pywraplp.Solver.CreateSolver('GLOP')
            if not solver:
                logger.error("Solver creation failed")
                return {"status": "error", "message": "Solver creation failed"}
            
            # Decision variables: allocation[resource_id][zone_id]
            allocation_vars = {}
            for resource in resources:
                for zone in zones:
                    var_name = f"alloc_{resource.id}_{zone.id}"
                    allocation_vars[(resource.id, zone.id)] = solver.NumVar(
                        0, resource.available_quantity, var_name
                    )
            
            # Constraints: Resource availability
            for resource in resources:
                resource_constraint = solver.Constraint(
                    0, resource.available_quantity,
                    f"resource_limit_{resource.id}"
                )
                for zone in zones:
                    if (resource.id, zone.id) in allocation_vars:
                        resource_constraint.SetCoefficient(
                            allocation_vars[(resource.id, zone.id)], 1
                        )
            
            # Constraints: Zone demand
            for zone in zones:
                demand = zone_demands.get(zone.id, {})
                # Aggregate compatible resources
                demand_qty = sum(demand.values()) / 10 if demand else 0
                
                zone_constraint = solver.Constraint(
                    0, demand_qty * 1.5,  # Allow 50% overage
                    f"zone_demand_{zone.id}"
                )
                for resource in resources:
                    if (resource.id, zone.id) in allocation_vars:
                        zone_constraint.SetCoefficient(
                            allocation_vars[(resource.id, zone.id)], 1
                        )
            
            # Objective: Maximize impact (priority × fulfilled demand - distance penalty)
            objective = solver.Objective()
            
            for resource in resources:
                for zone in zones:
                    if (resource.id, zone.id) in allocation_vars:
                        var = allocation_vars[(resource.id, zone.id)]
                        priority = priorities.get(zone.id, 0.5)
                        
                        # Route cost
                        route = self.routing_engine.calculate_route(
                            (resource.latitude, resource.longitude),
                            (zone.latitude, zone.longitude),
                            db
                        )
                        distance = route.get("distance", 50)
                        distance_penalty = max(0, distance / 100)  # Normalized
                        
                        # Benefit: priority weight
                        # Cost: distance penalty
                        coefficient = priority * 100 - distance_penalty * 2
                        objective.SetCoefficient(var, coefficient)
            
            objective.SetMaximization()
            
            # Solve
            status = solver.Solve()
            
            if status != pywraplp.Solver.OPTIMAL:
                logger.warning(f"Optimization status: {status}")
            
            # Extract solution
            allocations = []
            total_allocated = 0
            total_population_served = 0
            
            for resource in resources:
                for zone in zones:
                    if (resource.id, zone.id) in allocation_vars:
                        var = allocation_vars[(resource.id, zone.id)]
                        quantity = int(var.solution_value())
                        
                        if quantity > 0:
                            route = self.routing_engine.calculate_route(
                                (resource.latitude, resource.longitude),
                                (zone.latitude, zone.longitude),
                                db
                            )
                            
                            allocations.append({
                                "resource_id": resource.id,
                                "resource_name": resource.name,
                                "zone_id": zone.id,
                                "zone_name": zone.name,
                                "quantity": quantity,
                                "distance": route.get("distance", 0),
                                "travel_time_minutes": route.get("travel_time_minutes", 0),
                                "priority_score": priorities.get(zone.id, 0)
                            })
                            
                            total_allocated += quantity
                            # Rough estimate: 1 unit serves 10 people
                            total_population_served += quantity * 10
            
            unserved_population = max(
                0,
                sum(z.affected_population for z in zones) - total_population_served
            )
            
            avg_response_time = (
                sum(a["travel_time_minutes"] for a in allocations) / len(allocations)
                if allocations else 0
            )
            
            return {
                "status": "optimized",
                "scenario_id": scenario_id,
                "total_resources_allocated": total_allocated,
                "estimated_response_time_minutes": round(avg_response_time, 2),
                "estimated_population_served": total_population_served,
                "unserved_population": unserved_population,
                "allocations": allocations,
                "objective_value": objective.Value()
            }
        
        except Exception as e:
            logger.error(f"Optimization error: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
