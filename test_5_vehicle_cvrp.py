"""
===============================================================================
TEST 5-VEHICLE EXPANDED CAPACITY CVRP
===============================================================================
"""
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from backend.services.distance_service import get_road_matrix

def test_5_vehicle_cvrp():
    dist_matrix, _, _ = get_road_matrix()
    demands = [0, 14365, 13670, 12648, 12195, 11427, 10922, 12985, 10441]
    
    # 5 Vehicles with +10 Tons capacity added: 20t, 22t, 25t, 28t, 30t (Total = 125 Tons)
    capacities = [20000, 22000, 25000, 28000, 30000]

    num_locations = len(demands)
    num_vehicles = len(capacities)

    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_idx, to_idx):
        f_node = manager.IndexToNode(from_idx)
        t_node = manager.IndexToNode(to_idx)
        return int(round(dist_matrix[f_node][t_node] * 1000))

    transit_cb = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_cb)

    def demand_callback(from_idx):
        f_node = manager.IndexToNode(from_idx)
        return demands[f_node]

    demand_cb = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(demand_cb, 0, capacities, True, "Capacity")

    # Add disjunction to allow solver flexibility if needed
    for i in range(1, num_locations):
        routing.AddDisjunction([manager.NodeToIndex(i)], 100000)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.time_limit.seconds = 2

    sol = routing.SolveWithParameters(params)
    print("5-Vehicle OR-Tools Solved:", sol is not None)

    if sol:
        for v in range(num_vehicles):
            idx = routing.Start(v)
            route = []
            while not routing.IsEnd(idx):
                node = manager.IndexToNode(idx)
                route.append(node)
                idx = sol.Value(routing.NextVar(idx))
            route.append(manager.IndexToNode(idx))
            if len(route) > 2:
                print(f"Vehicle {v+1} (Cap: {capacities[v]} kg): Path = {route}")

if __name__ == "__main__":
    test_5_vehicle_cvrp()
