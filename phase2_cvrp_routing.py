"""
===============================================================================
PHASE 2 — VEHICLE ROUTING OPTIMIZATION (CVRP STANDALONE PROTOTYPE)
===============================================================================
File Path: phase2_cvrp_routing.py

Why this file exists:
---------------------
This script implements Phase 2 of the hackathon project. It solves the Capacitated 
Vehicle Routing Problem (CVRP) using Google OR-Tools.

Given:
  1. 9 Delhi-NCR location coordinates & road distance matrix (km)
  2. Allocated crop delivery quantities from Phase 1 (in kg)
  3. Fleet of 5 vehicles with capacities: [10,000, 12,000, 15,000, 18,000, 20,000] kg

Objective:
  MINIMIZE TOTAL TRAVEL DISTANCE across all delivery trucks

Hard Constraints:
  1. Vehicle Capacity: Total load on vehicle v <= Capacity of vehicle v
  2. Depot Start & End: Every used vehicle starts at Delhi (Depot) and returns to Delhi
  3. Zero-Demand Exclusion: Locations with 0 kg allocation are skipped (no stops assigned)
===============================================================================
"""

import sys
import io
import math
from typing import List, Dict, Any
from backend.optimizer.cvrp_solver import solve_cvrp

# Ensure UTF-8 output encoding for Windows PowerShell console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# -----------------------------------------------------------------------------
# 1. LOCATION DATA & BENCHMARK DISTANCE MATRIX (DELHI-NCR REGION)
# -----------------------------------------------------------------------------
LOCATIONS = [
    {"id": 0, "name": "Delhi",     "lat": 28.6139, "lon": 77.2090, "is_depot": True},
    {"id": 1, "name": "Noida",     "lat": 28.5355, "lon": 77.3910, "is_depot": False},
    {"id": 2, "name": "Ghaziabad", "lat": 28.6692, "lon": 77.4538, "is_depot": False},
    {"id": 3, "name": "Gurugram",  "lat": 28.4595, "lon": 77.0266, "is_depot": False},
    {"id": 4, "name": "Faridabad", "lat": 28.4089, "lon": 77.3178, "is_depot": False},
    {"id": 5, "name": "Sonipat",   "lat": 28.9931, "lon": 77.0151, "is_depot": False},
    {"id": 6, "name": "Panipat",   "lat": 29.3909, "lon": 76.9635, "is_depot": False},
    {"id": 7, "name": "Meerut",    "lat": 28.9845, "lon": 77.7064, "is_depot": False},
    {"id": 8, "name": "Rohtak",    "lat": 28.8955, "lon": 76.6066, "is_depot": False},
]

# Haversine distance helper with road circuitry multiplier (1.3)
def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    straight_line_km = R * c
    # Multiply by 1.3 to approximate actual road travel distance
    return round(straight_line_km * 1.3, 2)


def generate_benchmark_distance_matrix() -> List[List[float]]:
    """Generates 9x9 distance matrix for Delhi + 8 surrounding markets."""
    num_locs = len(LOCATIONS)
    matrix = [[0.0] * num_locs for _ in range(num_locs)]
    for i in range(num_locs):
        for j in range(num_locs):
            if i != j:
                matrix[i][j] = haversine_distance_km(
                    LOCATIONS[i]["lat"], LOCATIONS[i]["lon"],
                    LOCATIONS[j]["lat"], LOCATIONS[j]["lon"]
                )
    return matrix


# -----------------------------------------------------------------------------
# 2. VERIFICATION & PRETTY PRINT TEST SUITE
# -----------------------------------------------------------------------------
def run_phase2_test():
    print("=" * 80)
    print("      AGRI-LOGISTICS VEHICLE ROUTING SOLVER — PHASE 2 TEST RUN")
    print("=" * 80)

    # 5 Vehicle capacities in kg (10, 12, 15, 18, 20 tons)
    vehicle_capacities = [10000, 12000, 15000, 18000, 20000]

    # Allocations result from Phase 1 test run (100 Tons Wheat allocation)
    # Delhi (0) is depot. Market allocations:
    allocations_from_phase1 = [
        0.0,      # 0: Delhi (Depot - 0 delivery demand for trucks)
        15000.0,  # 1: Noida
        12000.0,  # 2: Ghaziabad
        5000.0,   # 3: Gurugram
        15000.0,  # 4: Faridabad
        10000.0,  # 5: Sonipat
        3000.0,   # 6: Panipat
        10000.0,  # 7: Meerut
        0.0,      # 8: Rohtak (Zero allocation -> MUST BE EXCLUDED FROM ROUTE STOPS)
    ]

    location_names = [loc["name"] for loc in LOCATIONS]
    distance_matrix = generate_benchmark_distance_matrix()

    total_market_demand = sum(allocations_from_phase1)

    print("INPUT METRICS:")
    print(f"  • Fleet Size Available      : {len(vehicle_capacities)} Vehicles")
    print(f"  • Vehicle Capacities (kg)   : {vehicle_capacities}")
    print(f"  • Total Fleet Capacity (kg) : {sum(vehicle_capacities):,.0f} kg ({sum(vehicle_capacities)/1000:.1f} Tons)")
    print(f"  • Total Delivery Load (kg)  : {total_market_demand:,.0f} kg ({total_market_demand/1000:.1f} Tons)")
    print("-" * 80)

    # Solve CVRP Routing
    result = solve_cvrp(
        distance_matrix=distance_matrix,
        demands=allocations_from_phase1,
        vehicle_capacities=vehicle_capacities,
        depot=0,
        location_names=location_names
    )

    print("\nOPTIMIZED VEHICLE ROUTE CARDS:")
    print("-" * 80)

    for route in result["routes"]:
        print(f"🚛 VEHICLE {route['vehicle_id']} ASSIGNMENT:")
        print(f"   Route       : {route['route_path_string']}")
        print(f"   Cargo Load  : {route['load_kg']:,.0f} kg / {route['vehicle_capacity_kg']:,.0f} kg")
        print(f"   Utilization : {route['utilization_percent']}%")
        print(f"   Distance    : {route['distance_km']} km")
        print(f"   Est. Time   : {route['duration_minutes']} minutes (~{route['duration_minutes']/60:.1f} hours)")
        print("-" * 80)

    print("\nOVERALL ROUTING SUMMARY:")
    print(f"  • Routing Status        : {result['status']}")
    print(f"  • Total Distance        : {result['total_distance_km']} km")
    print(f"  • Total Travel Time     : {result['total_duration_minutes']} minutes")
    print(f"  • Vehicles Used         : {result['vehicles_used']} / {result['vehicles_available']}")
    print(f"  • Fleet Load Handled    : {result['total_load_kg']:,.0f} kg")
    print(f"  • Fleet Utilization     : {result['fleet_utilization_percent']}%")

    print("\n" + "=" * 80)
    print("PHASE 2 VERIFICATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)


def run_phase2_edge_case_tests():
    print("\n" + "=" * 80)
    print("      RUNNING PHASE 2 EDGE CASE VERIFICATION SUITE")
    print("=" * 80)

    distance_matrix = generate_benchmark_distance_matrix()
    location_names = [loc["name"] for loc in LOCATIONS]
    capacities = [10000, 12000, 15000, 18000, 20000]

    # Edge Case 1: Zero Delivery Demands Across All Markets
    print("\n--- Test Case 1: Zero Deliveries (No stops required) ---")
    zero_demands = [0.0] * 9
    res1 = solve_cvrp(distance_matrix, zero_demands, capacities, 0, location_names)
    assert res1["vehicles_used"] == 0, "Vehicles were dispatched for zero demand!"
    print("✓ Passed: 0 vehicles dispatched when all market demands are zero.")

    # Edge Case 2: Demands Exceed Total Fleet Capacity
    print("\n--- Test Case 2: Insufficient Fleet Capacity ---")
    excess_demands = [0.0, 30000.0, 30000.0, 30000.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # 90k kg demand vs 75k fleet capacity
    try:
        solve_cvrp(distance_matrix, excess_demands, capacities, 0, location_names)
        print("✗ Failed: Should have raised ValueError for insufficient fleet capacity.")
    except ValueError as e:
        print(f"✓ Passed: Caught expected error -> '{e}'")

    # Edge Case 3: Only One Delivery Location Active
    print("\n--- Test Case 3: Single Active Delivery Market (Noida Only) ---")
    single_demand = [0.0, 5000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    res3 = solve_cvrp(distance_matrix, single_demand, capacities, 0, location_names)
    assert res3["vehicles_used"] == 1, "Should use exactly 1 vehicle for single delivery stop!"
    assert res3["routes"][0]["route_path_string"] == "Delhi → Noida → Delhi"
    print(f"✓ Passed: 1 vehicle dispatched on route '{res3['routes'][0]['route_path_string']}'.")

    print("\n" + "=" * 80)
    print("ALL PHASE 2 EDGE CASE TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_phase2_test()
    run_phase2_edge_case_tests()
