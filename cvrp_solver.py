# cvrp_solver.py
"""
Capacitated Vehicle Routing Problem (CVRP) Solver using Google OR-Tools.

Separation of Concerns:
- This module ONLY handles vehicle routing optimization.
- It receives a distance matrix, demands, and vehicle capacities.
- It ignores stops with 0 demand (except depot) so vehicles don't make unnecessary stops.
- It returns structured route assignments with capacity utilization and metrics.
"""

from ortools.constraint_solver import (
    pywrapcp,
    routing_enums_pb2
)


def solve_cvrp(
    distance_matrix,
    demands,
    vehicle_capacities,
    depot=0,
    location_names=None
):
    """
    Solves the CVRP problem.

    Parameters:
    - distance_matrix (list of list of float): Full NxN road distance matrix (in km)
    - demands (list of float/int): Demand at each location in kg
    - vehicle_capacities (list of float/int): Capacity of each vehicle in kg
    - depot (int): Index of the depot (default is 0)
    - location_names (list of str, optional): Names of locations for readable routes

    Returns:
    - dict: Structured solution containing per-vehicle routes and overall totals.
    """
    total_demand = sum(demands)
    total_capacity = sum(vehicle_capacities)

    # 1. Capacity Feasibility Check
    if total_demand > total_capacity:
        return {
            "error": "Insufficient vehicle capacity",
            "total_demand_kg": total_demand,
            "total_capacity_kg": total_capacity,
            "routes": [],
            "total_distance_km": 0,
            "total_load_kg": 0
        }

    # 2. Filter Active Locations (Depot + any location with demand > 0)
    # Zero-demand locations should not be visited by delivery trucks.
    active_indices = [depot] + [
        i for i in range(len(demands))
        if i != depot and demands[i] > 0
    ]

    # If no locations need delivery
    if len(active_indices) == 1:
        return {
            "routes": [],
            "total_distance_km": 0.0,
            "total_load_kg": 0,
            "vehicles_used": 0,
            "vehicles_available": len(vehicle_capacities)
        }

    # 3. Create sub-distance matrix & sub-demands for active locations only
    active_distance_matrix = [
        [distance_matrix[orig][dest] for dest in active_indices]
        for orig in active_indices
    ]
    active_demands = [int(demands[i]) for i in active_indices]

    num_active_locations = len(active_indices)
    num_vehicles = len(vehicle_capacities)
    active_depot_index = 0  # Depot is always first in active_indices

    # 4. Create OR-Tools Routing Index Manager & Routing Model
    manager = pywrapcp.RoutingIndexManager(
        num_active_locations,
        num_vehicles,
        active_depot_index
    )
    routing = pywrapcp.RoutingModel(manager)

    # 5. Distance Callback (Transit cost)
    # OR-Tools requires integer costs, so we convert km -> meters (integer)
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        distance_km = active_distance_matrix[from_node][to_node]
        return int(round(distance_km * 1000))

    distance_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)

    # 6. Demand Callback & Capacity Constraint
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return active_demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        [int(cap) for cap in vehicle_capacities],  # vehicle maximum capacities
        True,  # start cumul to zero
        "Capacity"
    )

    # 7. Search Strategy & Parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = 5

    # 8. Solve the Problem
    solution = routing.SolveWithParameters(search_parameters)

    if solution is None:
        return None

    # 9. Extract Structured Routes
    routes = []
    total_distance_m = 0
    total_load = 0

    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route_nodes_global = []
        route_names = []
        route_load = 0
        route_distance_m = 0

        while not routing.IsEnd(index):
            active_node = manager.IndexToNode(index)
            global_node = active_indices[active_node]
            route_nodes_global.append(global_node)

            if location_names:
                route_names.append(location_names[global_node])
            else:
                route_names.append(f"Node_{global_node}")

            route_load += demands[global_node]

            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance_m += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )

        # Add final return to depot
        active_end_node = manager.IndexToNode(index)
        global_end_node = active_indices[active_end_node]
        route_nodes_global.append(global_end_node)
        if location_names:
            route_names.append(location_names[global_end_node])
        else:
            route_names.append(f"Node_{global_end_node}")

        # If vehicle only went Depot -> Depot, it is unused
        if len(route_nodes_global) <= 2:
            continue

        route_distance_km = route_distance_m / 1000.0
        capacity = vehicle_capacities[vehicle_id]
        utilization = (route_load / capacity) * 100 if capacity > 0 else 0.0

        route_data = {
            "vehicle_id": vehicle_id + 1,
            "route_nodes": route_nodes_global,
            "route_names": route_names,
            "load_kg": route_load,
            "capacity_kg": capacity,
            "utilization_percent": round(utilization, 2),
            "distance_km": round(route_distance_km, 2)
        }
        routes.append(route_data)
        total_distance_m += route_distance_m
        total_load += route_load

    return {
        "routes": routes,
        "total_distance_km": round(total_distance_m / 1000.0, 2),
        "total_load_kg": total_load,
        "vehicles_used": len(routes),
        "vehicles_available": num_vehicles
    }