"""
TEST OR-TOOLS ROUTING PARAMETERS
"""
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from backend.services.distance_service import get_road_matrix

def test_ortools_strategies():
    dist_matrix, _, _ = get_road_matrix()
    demands = [0, 14365, 13670, 12648, 12195, 11427, 10922, 12985, 10441]
    capacities = [10000, 12000, 15000, 18000, 20000, 15000, 18000, 20000, 10000, 10000]

    num_locations = len(demands)
    num_vehicles = len(capacities)

    for strategy in [
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION,
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC,
        routing_enums_pb2.FirstSolutionStrategy.SAVINGS,
        routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC,
    ]:
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

        params = pywrapcp.DefaultRoutingSearchParameters()
        params.first_solution_strategy = strategy
        params.time_limit.seconds = 2

        sol = routing.SolveWithParameters(params)
        print(f"Strategy {strategy}: Solved = {sol is not None}")

if __name__ == "__main__":
    test_ortools_strategies()
