"""
===============================================================================
DEBUG CVRP SOLVER ERROR SCRIPT
===============================================================================
"""
import traceback
from backend.optimizer.cvrp_solver import solve_cvrp
from backend.data.locations import LOCATIONS

def test_failing_cvrp():
    # Demands from Wheat allocation (Delhi = 22,497 kg, Noida = 14,365 kg, etc.)
    demands = [0.0, 14365.36, 13670.56, 12648.88, 12195.6, 11427.04, 10922.08, 12985.6, 10441.84]
    capacities = [10000, 12000, 15000, 18000, 20000, 15000, 18000, 20000, 10000, 10000]
    
    # Distance matrix (Haversine/OSRM)
    from backend.services.distance_service import get_road_matrix
    dist_matrix, dur_matrix, _ = get_road_matrix()

    print("Demands:", demands)
    print("Max demand:", max(demands))
    print("Max capacity:", max(capacities))
    print("Total demand:", sum(demands))
    print("Total capacity:", sum(capacities))

    try:
        res = solve_cvrp(dist_matrix, demands, capacities, 0, [l["name"] for l in LOCATIONS], dur_matrix)
        print("CVRP Result Status:", res["status"])
        print("Routes count:", len(res["routes"]))
    except Exception as e:
        print("CVRP EXCEPTION:", e)
        traceback.print_exc()

if __name__ == "__main__":
    test_failing_cvrp()
