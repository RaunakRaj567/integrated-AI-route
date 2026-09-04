"""
===============================================================================
BACKEND OPTIMIZER MODULE — PROFIT OPTIMIZATION SERVICE
===============================================================================
File Path: backend/optimizer/profit_optimizer.py

Why this file exists:
---------------------
This module encapsulates the Phase 1 Linear Programming Profit Optimization 
engine for integration with FastAPI API routes and full-stack services.
===============================================================================
"""

from typing import Dict, Any, Optional
from ortools.linear_solver import pywraplp

LOCATIONS = [
    {"id": 0, "name": "Delhi",     "lat": 28.6139, "lon": 77.2090, "is_depot": True,  "est_km_from_depot": 0.0},
    {"id": 1, "name": "Noida",     "lat": 28.5355, "lon": 77.3910, "is_depot": False, "est_km_from_depot": 25.0},
    {"id": 2, "name": "Ghaziabad", "lat": 28.6692, "lon": 77.4538, "is_depot": False, "est_km_from_depot": 30.0},
    {"id": 3, "name": "Gurugram",  "lat": 28.4595, "lon": 77.0266, "is_depot": False, "est_km_from_depot": 30.0},
    {"id": 4, "name": "Faridabad", "lat": 28.4089, "lon": 77.3178, "is_depot": False, "est_km_from_depot": 35.0},
    {"id": 5, "name": "Sonipat",   "lat": 28.9931, "lon": 77.0151, "is_depot": False, "est_km_from_depot": 45.0},
    {"id": 6, "name": "Panipat",   "lat": 29.3909, "lon": 76.9635, "is_depot": False, "est_km_from_depot": 85.0},
    {"id": 7, "name": "Meerut",    "lat": 28.9845, "lon": 77.7064, "is_depot": False, "est_km_from_depot": 70.0},
    {"id": 8, "name": "Rohtak",    "lat": 28.8955, "lon": 76.6066, "is_depot": False, "est_km_from_depot": 75.0},
]

TRANSPORT_COST_PER_KG_KM = 0.20  # ₹10.00 per Ton / km (realistic commercial freight)

def estimate_logistics_cost_per_kg(distance_km: float) -> float:
    if distance_km <= 0:
        return 0.0
    return round(distance_km * TRANSPORT_COST_PER_KG_KM, 2)

def solve_profit_allocation(
    crop: str,
    available_quantity_kg: float,
    predicted_prices: Dict[str, float],
    expected_demands: Dict[str, float],
    price_adjustment_percent: float = 0.0,
    farmer_minimums: Optional[Dict[str, float]] = None,
    coverage_mode: str = "maximum_profit"
) -> Dict[str, Any]:
    farmer_minimums = farmer_minimums or {}

    if available_quantity_kg <= 0:
        raise ValueError(f"Available supply must be greater than 0 kg. Provided: {available_quantity_kg} kg.")

    if price_adjustment_percent > 10.0:
        raise ValueError(
            f"Price adjustment of +{price_adjustment_percent:.1f}% exceeds the maximum allowed limit of +10.0%."
        )

    markup_multiplier = 1.0 + (price_adjustment_percent / 100.0)

    total_mandatory_min = sum(farmer_minimums.values())
    if total_mandatory_min > available_quantity_kg:
        raise ValueError(
            f"Infeasible farmer preferences: Sum of mandated minimums ({total_mandatory_min:,.0f} kg) "
            f"exceeds available supply ({available_quantity_kg:,.0f} kg)."
        )

    for loc_name, req_min in farmer_minimums.items():
        market_demand = expected_demands.get(loc_name, 0.0)
        if req_min > market_demand:
            raise ValueError(
                f"Infeasible preference for {loc_name}: Mandated minimum ({req_min:,.0f} kg) "
                f"exceeds expected market demand ({market_demand:,.0f} kg)."
            )

    solver = pywraplp.Solver.CreateSolver('GLOP')
    if not solver:
        raise RuntimeError("Could not create OR-Tools GLOP solver instance.")

    alloc_vars = {}
    market_details_input = {}

    for loc in LOCATIONS:
        name = loc["name"]
        pred_price = predicted_prices.get(name, 0.0)
        demand = max(0.0, expected_demands.get(name, 0.0))
        final_price = round(pred_price * markup_multiplier, 2)
        transport_cost_per_kg = estimate_logistics_cost_per_kg(loc["est_km_from_depot"])
        net_contrib_per_kg = final_price - transport_cost_per_kg

        min_bound = farmer_minimums.get(name, 0.0)
        max_bound = demand
        if min_bound > max_bound:
            min_bound = max_bound

        var = solver.NumVar(min_bound, max_bound, f"alloc_{name}")
        alloc_vars[name] = var

        market_details_input[name] = {
            "predicted_price": pred_price,
            "final_price": final_price,
            "demand": demand,
            "transport_cost_per_kg": transport_cost_per_kg,
            "net_contrib_per_kg": net_contrib_per_kg,
            "is_depot": loc["is_depot"],
            "lat": loc["lat"],
            "lon": loc["lon"]
        }

    supply_constraint = solver.Constraint(0, available_quantity_kg, "TotalSupplyConstraint")
    for var in alloc_vars.values():
        supply_constraint.SetCoefficient(var, 1.0)

    objective = solver.Objective()
    for name, var in alloc_vars.items():
        contrib = market_details_input[name]["net_contrib_per_kg"]
        if coverage_mode == "balanced_distribution" and contrib > 0:
            contrib += 0.001
        objective.SetCoefficient(var, contrib)
    
    objective.SetMaximization()

    status = solver.Solve()
    if status != pywraplp.Solver.OPTIMAL and status != pywraplp.Solver.FEASIBLE:
        raise RuntimeError("Optimizer failed to find a feasible allocation solution.")

    allocated_markets = []
    total_allocated_kg = 0.0
    total_expected_revenue = 0.0
    total_est_logistics_cost = 0.0
    total_expected_net_profit = 0.0
    total_expected_demand_kg = sum(details["demand"] for details in market_details_input.values())

    explainability_notes = []

    for name, var in alloc_vars.items():
        qty_kg = round(var.solution_value(), 2)
        if qty_kg < 0.01:
            qty_kg = 0.0

        details = market_details_input[name]
        pred_price = details["predicted_price"]
        final_price = details["final_price"]
        demand_kg = details["demand"]
        t_cost_per_kg = details["transport_cost_per_kg"]
        net_contrib = details["net_contrib_per_kg"]

        revenue = round(qty_kg * final_price, 2)
        transport_cost = round(qty_kg * t_cost_per_kg, 2)
        net_profit = round(revenue - transport_cost, 2)
        unfulfilled_demand = round(max(0.0, demand_kg - qty_kg), 2)

        total_allocated_kg += qty_kg
        total_expected_revenue += revenue
        total_est_logistics_cost += transport_cost
        total_expected_net_profit += net_profit

        if qty_kg > 0:
            if name in farmer_minimums:
                status_str = "Farmer Mandated"
                reason_str = f"Mandated by farmer preferences ({farmer_minimums[name]:,.0f} kg min)."
            else:
                status_str = "Allocated"
                reason_str = (
                    f"High expected contribution (₹{net_contrib:.2f}/kg net) "
                    f"and available market demand ({demand_kg:,.0f} kg)."
                )
        else:
            if demand_kg == 0:
                status_str = "Zero Demand"
                reason_str = "No expected market demand on this date."
            elif net_contrib <= 0:
                status_str = "Unprofitable"
                reason_str = (
                    f"Selling price (₹{final_price:.2f}/kg) is lower than or equal to "
                    f"estimated logistics cost (₹{t_cost_per_kg:.2f}/kg)."
                )
            else:
                status_str = "Low Priority"
                reason_str = "Sufficient supply allocated to higher net contribution markets first."

        allocated_markets.append({
            "location": name,
            "is_depot": details["is_depot"],
            "latitude": details["lat"],
            "longitude": details["lon"],
            "predicted_price_per_kg": pred_price,
            "final_price_per_kg": final_price,
            "expected_demand_kg": demand_kg,
            "allocated_kg": qty_kg,
            "allocated_tons": round(qty_kg / 1000.0, 3),
            "est_transport_cost_per_kg": t_cost_per_kg,
            "expected_net_contrib_per_kg": round(net_contrib, 2),
            "expected_revenue": revenue,
            "estimated_logistics_cost": transport_cost,
            "expected_net_profit": net_profit,
            "unfulfilled_demand_kg": unfulfilled_demand,
            "status": status_str,
            "explainability": reason_str
        })

        explainability_notes.append(f"• {name} ({status_str}): {reason_str}")

    surplus_kg = round(max(0.0, available_quantity_kg - total_allocated_kg), 2)
    total_unfulfilled_demand_kg = round(max(0.0, total_expected_demand_kg - total_allocated_kg), 2)
    margin_percent = round((total_expected_net_profit / total_expected_revenue * 100.0), 2) if total_expected_revenue > 0 else 0.0

    has_profitable_market = any(m["allocated_kg"] > 0 for m in allocated_markets)
    overall_status = "Optimal Allocation Found" if has_profitable_market else "No Profitable Allocation Found"

    return {
        "crop": crop,
        "status": overall_status,
        "price_adjustment_percent": price_adjustment_percent,
        "coverage_mode": coverage_mode,
        "supply": {
            "available_kg": available_quantity_kg,
            "available_tons": round(available_quantity_kg / 1000.0, 3),
            "allocated_kg": round(total_allocated_kg, 2),
            "allocated_tons": round(total_allocated_kg / 1000.0, 3),
            "surplus_kg": surplus_kg,
            "surplus_tons": round(surplus_kg / 1000.0, 3),
            "total_expected_demand_kg": total_expected_demand_kg,
            "unfulfilled_demand_kg": total_unfulfilled_demand_kg
        },
        "profit_summary": {
            "expected_revenue": round(total_expected_revenue, 2),
            "estimated_logistics_cost": round(total_est_logistics_cost, 2),
            "expected_net_profit": round(total_expected_net_profit, 2),
            "expected_margin_percent": margin_percent
        },
        "markets": allocated_markets,
        "explainability_summary": explainability_notes
    }
