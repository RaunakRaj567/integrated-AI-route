"""
===============================================================================
ROUTING SERVICE MODULE (CVRP + OSRM MATRIX & GEOMETRY)
===============================================================================
File Path: backend/services/routing_service.py

Why this file exists:
---------------------
Orchestrates CVRP route optimization, OSRM road distance matrix fetching, and 
OSRM GeoJSON route geometry generation for FastAPI API routes.
===============================================================================
"""

from typing import Dict, Any, List, Optional
from backend.optimizer.cvrp_solver import solve_cvrp
from backend.services.distance_service import get_road_matrix
from backend.services.geometry_service import get_route_geometry
from backend.data.locations import LOCATIONS
from backend.data.vehicle_data import DEFAULT_VEHICLE_CAPACITIES


def run_routing_service(
    allocations_map: Dict[str, float],
    vehicle_capacities: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Executes full routing service for given allocation map (e.g. {"Noida": 15000, ...}).

    Steps:
      1. Fetch OSRM distance & duration matrix for 9 locations.
      2. Convert allocation dict to demands vector for Delhi + 8 markets.
      3. Solve CVRP vehicle routing using OR-Tools.
      4. Fetch GeoJSON LineString geometry for each vehicle route via OSRM.
      5. Return structured routing solution.
    """
    vehicle_caps = vehicle_capacities or DEFAULT_VEHICLE_CAPACITIES
    location_names = [loc["name"] for loc in LOCATIONS]

    # Fetch OSRM road matrices
    dist_matrix, dur_matrix, matrix_source = get_road_matrix(timeout_seconds=5)

    # Prepare demands vector (Delhi depot = 0 delivery load)
    cvrp_demands = []
    for loc in LOCATIONS:
        name = loc["name"]
        if loc["is_depot"]:
            cvrp_demands.append(0.0)
        else:
            cvrp_demands.append(max(0.0, allocations_map.get(name, 0.0)))

    # Solve CVRP routing
    cvrp_result = solve_cvrp(
        distance_matrix=dist_matrix,
        demands=cvrp_demands,
        vehicle_capacities=vehicle_caps,
        depot=0,
        location_names=location_names,
        duration_matrix=dur_matrix
    )

    # Attach OSRM GeoJSON geometry to each vehicle route
    for route in cvrp_result["routes"]:
        nodes = route["route_nodes"]
        geo_info = get_route_geometry(nodes, timeout_seconds=5)
        route["geojson"] = geo_info["geometry"]
        route["geojson_source"] = geo_info["source"]

    return {
        "status": cvrp_result["status"],
        "routing_summary": {
            "vehicles_available": cvrp_result["vehicles_available"],
            "vehicles_used": cvrp_result["vehicles_used"],
            "total_distance_km": cvrp_result["total_distance_km"],
            "total_duration_minutes": cvrp_result["total_duration_minutes"],
            "total_load_kg": cvrp_result["total_load_kg"],
            "fleet_utilization_percent": cvrp_result["fleet_utilization_percent"]
        },
        "routes": cvrp_result["routes"],
        "matrix_source": matrix_source
    }
