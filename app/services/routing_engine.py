import math
from typing import List, Dict, Tuple
import networkx as nx
from sqlalchemy.orm import Session
from app.models.road import Road, RoadStatus
from app.models.zone import AffectedZone
from app.models.facility import Facility

class RoutingEngine:
    """Handle routing and path finding using NetworkX."""
    
    def __init__(self):
        self.graph = None
        self.edge_data = {}
    
    def build_graph(self, db: Session):
        """
        Build NetworkX graph from roads in database.
        """
        self.graph = nx.DiGraph()
        roads = db.query(Road).filter(Road.status != RoadStatus.BLOCKED).all()
        
        for road in roads:
            weight = road.travel_time if road.travel_time > 0 else road.distance
            self.graph.add_edge(
                road.from_node,
                road.to_node,
                weight=weight,
                distance=road.distance,
                travel_time=road.travel_time,
                road_id=road.road_id,
                status=road.status
            )
            self.edge_data[(road.from_node, road.to_node)] = {
                "road_id": road.road_id,
                "distance": road.distance,
                "travel_time": road.travel_time
            }
    
    def calculate_route(self, from_coords: Tuple[float, float], 
                       to_coords: Tuple[float, float],
                       db: Session) -> Dict:
        """
        Calculate shortest route between two coordinates.
        
        Returns:
            Dict with distance, time, and path details
        """
        if self.graph is None:
            self.build_graph(db)
        
        # Find nearest nodes to coordinates
        from_node = self._nearest_node(from_coords, db)
        to_node = self._nearest_node(to_coords, db)
        
        if from_node is None or to_node is None:
            # Fallback to Euclidean distance
            dist = self._haversine_distance(from_coords, to_coords)
            time = dist / 50 * 60  # Assume 50 km/h average speed
            return {
                "distance": round(dist, 2),
                "travel_time_minutes": round(time, 2),
                "path_available": False,
                "blocked": False
            }
        
        try:
            path = nx.shortest_path(
                self.graph, 
                source=from_node, 
                target=to_node, 
                weight="weight"
            )
            
            # Calculate total distance and time
            total_distance = 0
            total_time = 0
            
            for i in range(len(path) - 1):
                edge_data = self.graph.edges[path[i], path[i+1]]
                total_distance += edge_data.get("distance", 0)
                total_time += edge_data.get("travel_time", 0)
            
            return {
                "distance": round(total_distance, 2),
                "travel_time_minutes": round(total_time, 2),
                "path_available": True,
                "blocked": False,
                "nodes": path
            }
        except nx.NetworkXNoPath:
            return {
                "distance": None,
                "travel_time_minutes": None,
                "path_available": False,
                "blocked": True,
                "error": "No path available"
            }
    
    def block_road(self, road_id: str, db: Session):
        """
        Block a road and rebuild graph.
        """
        road = db.query(Road).filter(Road.road_id == road_id).first()
        if road:
            road.status = RoadStatus.BLOCKED
            db.commit()
            self.graph = None  # Invalidate cache
    
    def restore_road(self, road_id: str, db: Session):
        """
        Restore a blocked road and rebuild graph.
        """
        road = db.query(Road).filter(Road.road_id == road_id).first()
        if road:
            road.status = RoadStatus.OPEN
            db.commit()
            self.graph = None  # Invalidate cache
    
    def _nearest_node(self, coords: Tuple[float, float], db: Session) -> str:
        """
        Find nearest road node to given coordinates.
        """
        roads = db.query(Road).filter(Road.status != RoadStatus.BLOCKED).all()
        if not roads:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for road in roads:
            # Check from_node
            dist = self._haversine_distance(
                coords, 
                (road.from_latitude, road.from_longitude)
            )
            if dist < min_distance:
                min_distance = dist
                nearest = road.from_node
        
        return nearest if min_distance < 10 else None  # Max 10 km
    
    @staticmethod
    def _haversine_distance(coord1: Tuple[float, float], 
                           coord2: Tuple[float, float]) -> float:
        """
        Calculate distance between two coordinates in km.
        """
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2)**2 + 
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
            math.sin(dlon / 2)**2
        )
        c = 2 * math.asin(math.sqrt(a))
        return R * c
