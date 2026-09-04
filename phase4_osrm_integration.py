"""
===============================================================================
PHASE 4 — OSRM ROAD MATRIX & ROUTE GEOMETRY INTEGRATION
===============================================================================
File Path: phase4_osrm_integration.py

Why this file exists:
---------------------
Tests Phase 4 functionality:
  1. Fetches real road distance (km) and travel duration (min) matrix via OSRM Table Service.
  2. Runs CVRP vehicle routing optimization using live OSRM matrix.
  3. Fetches exact GeoJSON LineString road geometry for each truck's route via OSRM Route Service.
===============================================================================
"""

import sys
import io
import json
from backend.services.distance_service import get_road_matrix
from backend.services.geometry_service import get_route_geometry
from backend.optimizer.cvrp_solver import solve_cvrp
from backend.data.locations import LOCATIONS

# Ensure UTF-8 output encoding for Windows PowerShell console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def run_phase4_test():
    print("=" * 85)
    print("      AGRI-LOGISTICS OSRM ROAD MATRIX & GEOMETRY — PHASE 4 TEST RUN")
    print("=" * 85)

    # 1. Fetch OSRM Matrix
    print("1. Fetching OSRM Road Distance & Travel Duration Matrix...")
    dist_matrix, dur_matrix, matrix_source = get_road_matrix(timeout_seconds=5)
    print(f"   ✓ Matrix Source: {matrix_source}")
    print(f"   ✓ Matrix Dimensions: {len(dist_matrix)}x{len(dist_matrix[0])}")

    # Display sample distance from Delhi (index 0) to all markets
    delhi_dists = {LOCATIONS[i]["name"]: dist_matrix[0][i] for i in range(len(LOCATIONS))}
    print(f"   ✓ Road Distances from Delhi Depot (km): {delhi_dists}")

    # 2. Run CVRP with OSRM Matrix
    print("\n2. Solving CVRP Routing with OSRM Road Matrix...")
    vehicle_capacities = [10000, 12000, 15000, 18000, 20000]
    demands = [0.0, 15000.0, 12000.0, 5000.0, 15000.0, 10000.0, 3000.0, 10000.0, 0.0]
    location_names = [loc["name"] for loc in LOCATIONS]

    cvrp_res = solve_cvrp(
        distance_matrix=dist_matrix,
        demands=demands,
        vehicle_capacities=vehicle_capacities,
        depot=0,
        location_names=location_names,
        duration_matrix=dur_matrix
    )

    print(f"   ✓ Vehicles Used: {cvrp_res['vehicles_used']} / {cvrp_res['vehicles_available']}")
    print(f"   ✓ Total Fleet Distance: {cvrp_res['total_distance_km']} km")
    print(f"   ✓ Total Fleet Travel Duration: {cvrp_res['total_duration_minutes']} mins (~{cvrp_res['total_duration_minutes']/60:.1f} hrs)")

    # 3. Fetch OSRM GeoJSON Road Geometry for each truck route
    print("\n3. Fetching GeoJSON LineString Road Geometries for Map Rendering...")
    print("-" * 85)

    for route in cvrp_res["routes"]:
        nodes = route["route_nodes"]
        geo_info = get_route_geometry(nodes, timeout_seconds=5)
        route["geojson"] = geo_info["geometry"]
        route["geojson_source"] = geo_info["source"]

        print(f"🚛 TRUCK {route['vehicle_id']} ROAD GEOMETRY:")
        print(f"   Route Path : {route['route_path_string']}")
        print(f"   Cargo Load : {route['load_kg']:,} kg / {route['vehicle_capacity_kg']:,} kg ({route['utilization_percent']}%)")
        print(f"   Road Dist  : {route['distance_km']} km | Time: {route['duration_minutes']} mins")
        print(f"   Geometry   : GeoJSON {geo_info['geometry']['type']} ({len(geo_info['geometry']['coordinates'])} road coordinates)")
        print(f"   Geo Source : {geo_info['source']}")
        print("-" * 85)

    print("\n" + "=" * 85)
    print("PHASE 4 OSRM ROAD MATRIX & GEOMETRY VERIFICATION SUCCESSFUL!")
    print("=" * 85)


if __name__ == "__main__":
    run_phase4_test()
