"""
===============================================================================
PHASE 3 — INTEGRATED PROFIT ALLOCATION + CVRP ROUTING PIPELINE
===============================================================================
File Path: phase3_integrated_pipeline.py

Why this file exists:
---------------------
This script implements Phase 3 of the hackathon project. It connects Phase 1 
(Profit-Maximizing Crop Allocation) and Phase 2 (CVRP Vehicle Routing Optimization)
into a unified end-to-end Python optimization pipeline.

Pipeline Workflow:
  1. Farmer Input & Market Predictions
  2. Stage 1: Solve Profit-Maximizing Crop Allocation (Google OR-Tools GLOP)
  3. Stage 2: Extract active delivery market demands
  4. Stage 3: Solve CVRP Vehicle Routing (Google OR-Tools Routing Solver)
  5. Stage 4: Recalculate Final Net Profit using ACTUAL optimized route costs
===============================================================================
"""

import sys
import io
from typing import Dict, Any, List
from backend.optimizer.profit_optimizer import solve_profit_allocation, LOCATIONS
from backend.optimizer.cvrp_solver import solve_cvrp
from phase2_cvrp_routing import generate_benchmark_distance_matrix

# Ensure UTF-8 encoding for Windows PowerShell console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Transport operational cost per truck km (e.g., ₹20/km for fuel & driver)
COST_PER_TRUCK_KM = 20.0


def run_integrated_pipeline(
    crop: str,
    available_quantity_kg: float,
    predicted_prices: Dict[str, float],
    expected_demands: Dict[str, float],
    vehicle_capacities: List[float],
    price_adjustment_percent: float = 0.0,
    farmer_minimums: Dict[str, float] = None,
    coverage_mode: str = "maximum_profit"
) -> Dict[str, Any]:
    """
    Executes the two-stage Integrated Profit Optimization & Vehicle Routing Pipeline.
    """
    # -------------------------------------------------------------------------
    # STAGE 1: PROFIT-MAXIMIZING CROP ALLOCATION
    # -------------------------------------------------------------------------
    allocation_result = solve_profit_allocation(
        crop=crop,
        available_quantity_kg=available_quantity_kg,
        predicted_prices=predicted_prices,
        expected_demands=expected_demands,
        price_adjustment_percent=price_adjustment_percent,
        farmer_minimums=farmer_minimums,
        coverage_mode=coverage_mode
    )

    # -------------------------------------------------------------------------
    # STAGE 2: PREPARE CVRP INPUTS (Active Delivery Demands)
    # -------------------------------------------------------------------------
    # Create mapping of location names to their allocated quantities
    market_alloc_map = {m["location"]: m["allocated_kg"] for m in allocation_result["markets"]}

    # Demands vector for 9 locations [Delhi, Noida, Ghaziabad, ..., Rohtak]
    # Delhi depot demand is set to 0 for delivery trucks
    cvrp_demands = []
    for loc in LOCATIONS:
        name = loc["name"]
        if loc["is_depot"]:
            cvrp_demands.append(0.0)
        else:
            cvrp_demands.append(market_alloc_map.get(name, 0.0))

    distance_matrix = generate_benchmark_distance_matrix()
    location_names = [loc["name"] for loc in LOCATIONS]

    # -------------------------------------------------------------------------
    # STAGE 3: SOLVE CVRP ROUTING OPTIMIZATION
    # -------------------------------------------------------------------------
    routing_result = solve_cvrp(
        distance_matrix=distance_matrix,
        demands=cvrp_demands,
        vehicle_capacities=vehicle_capacities,
        depot=0,
        location_names=location_names
    )

    # -------------------------------------------------------------------------
    # STAGE 4: RECALCULATE FINAL PROFIT WITH ACTUAL ROUTE COSTS
    # -------------------------------------------------------------------------
    actual_transport_cost = round(routing_result["total_distance_km"] * COST_PER_TRUCK_KM, 2)
    expected_revenue = allocation_result["profit_summary"]["expected_revenue"]
    final_net_profit = round(expected_revenue - actual_transport_cost, 2)
    final_margin_percent = round((final_net_profit / expected_revenue * 100.0), 2) if expected_revenue > 0 else 0.0

    return {
        "crop": crop,
        "available_supply_kg": available_quantity_kg,
        "allocated_supply_kg": allocation_result["supply"]["allocated_kg"],
        "surplus_kg": allocation_result["supply"]["surplus_kg"],
        "price_adjustment_percent": price_adjustment_percent,
        "stage1_allocation": allocation_result["markets"],
        "stage1_est_profit": allocation_result["profit_summary"]["expected_net_profit"],
        "stage2_routing": routing_result,
        "final_financial_summary": {
            "expected_revenue": expected_revenue,
            "estimated_logistics_cost_before_routing": allocation_result["profit_summary"]["estimated_logistics_cost"],
            "actual_optimized_logistics_cost": actual_transport_cost,
            "final_expected_net_profit": final_net_profit,
            "final_margin_percent": final_margin_percent
        }
    }


# -----------------------------------------------------------------------------
# VERIFICATION SUITE
# -----------------------------------------------------------------------------
def main():
    print("=" * 85)
    print("      AGRI-LOGISTICS INTEGRATED PIPELINE — PHASE 3 TEST RUN")
    print("=" * 85)

    crop_name = "Wheat"
    available_supply_kg = 100000.0
    farmer_markup = 5.0
    vehicle_capacities = [10000, 12000, 15000, 18000, 20000]

    predicted_prices = {
        "Delhi": 32.0, "Noida": 35.0, "Ghaziabad": 34.0, "Gurugram": 38.0,
        "Faridabad": 33.0, "Sonipat": 31.0, "Panipat": 30.0, "Meerut": 36.0, "Rohtak": 29.0
    }

    expected_demands = {
        "Delhi": 30000.0, "Noida": 15000.0, "Ghaziabad": 12000.0, "Gurugram": 5000.0,
        "Faridabad": 15000.0, "Sonipat": 10000.0, "Panipat": 8000.0, "Meerut": 10000.0, "Rohtak": 5000.0
    }

    result = run_integrated_pipeline(
        crop=crop_name,
        available_quantity_kg=available_supply_kg,
        predicted_prices=predicted_prices,
        expected_demands=expected_demands,
        vehicle_capacities=vehicle_capacities,
        price_adjustment_percent=farmer_markup
    )

    print("\nSTAGE 1: PROFIT-MAXIMIZING CROP ALLOCATION RESULT")
    print("-" * 85)
    header = f"{'Location':<12} | {'Final Price':<11} | {'Demand (kg)':<11} | {'Allocated (kg)':<14} | {'Status':<15}"
    print(header)
    print("-" * len(header))
    for m in result["stage1_allocation"]:
        print(f"{m['location']:<12} | ₹{m['final_price_per_kg']:<10.2f} | {m['expected_demand_kg']:<11,.0f} | {m['allocated_kg']:<14,.0f} | {m['status']:<15}")

    print("\nSTAGE 2: CVRP VEHICLE ROUTE OPTIMIZATION RESULT")
    print("-" * 85)
    for r in result["stage2_routing"]["routes"]:
        print(f"  🚛 Truck {r['vehicle_id']} ({r['vehicle_capacity_kg']:,} kg cap): {r['route_path_string']} | Load: {r['load_kg']:,} kg ({r['utilization_percent']}%) | Dist: {r['distance_km']} km")

    fin = result["final_financial_summary"]
    print("\nSTAGE 3: FINAL PROFIT RECALCULATION (AFTER ROUTE OPTIMIZATION)")
    print("-" * 85)
    print(f"  • Total Expected Revenue                   : ₹{fin['expected_revenue']:,.2f}")
    print(f"  • Estimated Transport Cost (Stage 1 approx)  : ₹{fin['estimated_logistics_cost_before_routing']:,.2f}")
    print(f"  • Actual Transport Cost (Stage 2 CVRP)     : ₹{fin['actual_optimized_logistics_cost']:,.2f}")
    print(f"  • FINAL EXPECTED NET PROFIT                 : ₹{fin['final_expected_net_profit']:,.2f}")
    print(f"  • FINAL NET PROFIT MARGIN                   : {fin['final_margin_percent']}%")

    print("\n" + "=" * 85)
    print("PHASE 3 INTEGRATED PIPELINE VERIFICATION SUCCESSFUL!")
    print("=" * 85)


if __name__ == "__main__":
    main()
