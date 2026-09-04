# main.py
"""
Phase 1: Standalone CVRP Logistics Engine
Tests:
1. Loading Locations & Demands
2. Fetching real OSRM road distance and duration matrix
3. Solving Capacitated Vehicle Routing Problem (CVRP) with Google OR-Tools
4. Fetching exact OSRM turn-by-turn road geometry for each route
"""

from locations import LOCATIONS, get_location_names
from distance_service import get_road_matrix
from cvrp_solver import solve_cvrp
from route_geometry import get_route_geometry


def main():
    print("=" * 70)
    print("AGRI-LOGISTICS DEMAND + CVRP ROUTE OPTIMIZATION ENGINE (PHASE 1)")
    print("=" * 70)

    # 1. VEHICLE FLEET CONFIGURATION
    vehicle_capacities = [
        10000,  # Vehicle 1: 10,000 kg (10 tons)
        12000,  # Vehicle 2: 12,000 kg (12 tons)
        15000,  # Vehicle 3: 15,000 kg (15 tons)
        18000,  # Vehicle 4: 18,000 kg (18 tons)
        20000   # Vehicle 5: 20,000 kg (20 tons)
    ]

    # 2. SAMPLE DEMANDS (in kg)
    # Node 0 = Delhi (Depot, Demand = 0)
    # Node 1 = Noida (4,200 kg)
    # Node 2 = Ghaziabad (7,100 kg)
    # Node 3 = Gurugram (0 kg - no delivery needed)
    # Node 4 = Faridabad (5,100 kg)
    # Node 5 = Sonipat (3,000 kg)
    # Node 6 = Panipat (8,000 kg)
    # Node 7 = Meerut (0 kg - no delivery needed)
    # Node 8 = Rohtak (6,000 kg)
    demands = [
        0,      # Delhi (Depot)
        4200,   # Noida
        7100,   # Ghaziabad
        0,      # Gurugram
        5100,   # Faridabad
        3000,   # Sonipat
        8000,   # Panipat
        0,      # Meerut
        6000    # Rohtak
    ]

    print("\n[Step 1] Initializing Locations & Demands:")
    location_names = get_location_names()
    for loc, demand in zip(LOCATIONS, demands):
        role = "DEPOT" if loc.get("is_depot") else "BUYER"
        print(f"  - [{loc['id']}] {loc['name']:<25} ({role:<5}): {demand:>5} kg")

    # 3. GET REAL ROAD DISTANCE + TIME MATRIX VIA OSRM
    print("\n[Step 2] Querying OSRM Table API for real road distance matrix...")
    try:
        distance_matrix, duration_matrix = get_road_matrix()
        print("  -> Road distance and time matrix fetched successfully!")
    except Exception as e:
        print(f"  [ERROR] Failed to fetch OSRM matrix: {e}")
        return

    # 4. RUN OR-TOOLS CVRP OPTIMIZATION
    print("\n[Step 3] Solving CVRP with Google OR-Tools...")
    result = solve_cvrp(
        distance_matrix=distance_matrix,
        demands=demands,
        vehicle_capacities=vehicle_capacities,
        depot=0,
        location_names=location_names
    )

    if result is None or "error" in result:
        print(f"\n[FAILED] Optimization error: {result.get('error', 'No feasible solution found.')}")
        return

    # 5. DISPLAY OPTIMIZED ROUTES & GET ROAD GEOMETRY
    print("\n" + "=" * 70)
    print("OPTIMIZED DELIVERY ROUTES")
    print("=" * 70)

    for route in result["routes"]:
        print(f"\n--- Vehicle {route['vehicle_id']} ---")
        print(f"  Route:       {' -> '.join(route['route_names'])}")
        print(f"  Load:        {route['load_kg']:,} kg / {route['capacity_kg']:,} kg")
        print(f"  Utilization: {route['utilization_percent']}%")
        print(f"  Matrix Dist: {route['distance_km']} km")

        # Fetch actual road geometry from OSRM
        try:
            geometry = get_route_geometry(route["route_nodes"])
            print(f"  OSRM Dist:   {geometry['distance_km']} km")
            print(f"  Est. Time:   {geometry['duration_minutes']} min ({int(geometry['duration_minutes'] // 60)}h {int(geometry['duration_minutes'] % 60)}m)")
        except Exception as e:
            print(f"  [WARNING] Could not fetch geometry: {e}")

    print("\n" + "=" * 70)
    print("FLEET & LOGISTICS SUMMARY")
    print("=" * 70)
    print(f"Total Demand Delivered: {result['total_load_kg']:,} kg")
    print(f"Total Road Distance:    {result['total_distance_km']} km")
    print(f"Vehicles Used:          {result['vehicles_used']} of {result['vehicles_available']} available")
    print("=" * 70)


if __name__ == "__main__":
    main()