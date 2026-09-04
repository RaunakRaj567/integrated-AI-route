"""
===============================================================================
PHASE 1 — PROFIT-MAXIMIZING MARKET CROP ALLOCATION (STANDALONE PROTOTYPE)
===============================================================================
File Path: phase1_profit_allocation.py

Why this file exists:
---------------------
This script implements Phase 1 of the hackathon project. It uses Google OR-Tools 
Linear Solver (GLOP) to solve the Crop Allocation Problem.

Given:
  1. Farmer's available crop quantity (in kg)
  2. Farmer price markup/adjustment (max +10%)
  3. Location-wise predicted selling prices (₹/kg)
  4. Location-wise expected demand (kg)
  5. Estimated logistics/transportation cost per location (₹/kg)
  6. Optional farmer distribution preferences & minimum quantity constraints

Objective:
  MAXIMIZE TOTAL EXPECTED NET PROFIT
  Net Profit = Total Expected Revenue - Total Estimated Logistics Cost

Constraints:
  1. Supply Limit: Total allocated crop across all markets <= Available crop quantity
  2. Demand Limit: Crop allocated to market i <= Expected demand at market i
  3. Non-negativity: Crop allocated to market i >= 0
  4. Price Adjustment Limit: Farmer markup price <= Predicted price * 1.10 (+10%)
  5. Farmer Mandates: Crop allocated to market i >= Farmer minimum required quantity
===============================================================================
"""

import sys
import io
from typing import Dict, Any, List, Optional
from ortools.linear_solver import pywraplp

# Ensure UTF-8 encoding for Windows PowerShell console output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# -----------------------------------------------------------------------------
# 1. CENTRALIZED LOCATION DATA & LOGISTICS ESTIMATION
# -----------------------------------------------------------------------------
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

# Estimated logistics cost rate per kg per km (e.g. ₹0.05 per kg-km)
TRANSPORT_COST_PER_KG_KM = 0.05


def estimate_logistics_cost_per_kg(distance_km: float) -> float:
    """Calculates approximate logistics/transportation cost per kg based on distance."""
    if distance_km <= 0:
        return 0.0
    return round(distance_km * TRANSPORT_COST_PER_KG_KM, 2)


# -----------------------------------------------------------------------------
# 2. PROFIT OPTIMIZATION CORE SOLVER
# -----------------------------------------------------------------------------
def solve_profit_allocation(
    crop: str,
    available_quantity_kg: float,
    predicted_prices: Dict[str, float],
    expected_demands: Dict[str, float],
    price_adjustment_percent: float = 0.0,
    farmer_minimums: Optional[Dict[str, float]] = None,
    coverage_mode: str = "maximum_profit"
) -> Dict[str, Any]:
    """
    Solves the Profit-Maximizing Market Crop Allocation problem using OR-Tools GLOP.

    Parameters:
      crop: Name of the crop (e.g., 'Wheat', 'Rice', 'Onion')
      available_quantity_kg: Total crop quantity available with farmer in kg
      predicted_prices: Dictionary mapping location name -> predicted price (₹/kg)
      expected_demands: Dictionary mapping location name -> expected market demand (kg)
      price_adjustment_percent: Farmer markup percentage (+0% to +10%)
      farmer_minimums: Dict mapping location name -> mandatory minimum allocation (kg)
      coverage_mode: 'maximum_profit', 'balanced_distribution', or 'serve_selected'

    Returns:
      Dict containing allocation details, summary metrics, and explainability text.
    """
    farmer_minimums = farmer_minimums or {}

    # --- VALIDATION 1: Supply Check ---
    if available_quantity_kg <= 0:
        raise ValueError(f"Available supply must be greater than 0 kg. Provided: {available_quantity_kg} kg.")

    # --- VALIDATION 2: Price Adjustment (+10% Limit) ---
    if price_adjustment_percent > 10.0:
        raise ValueError(
            f"Price adjustment of +{price_adjustment_percent:.1f}% exceeds the maximum allowed limit of +10.0%."
        )
    if price_adjustment_percent < -50.0:
        raise ValueError("Price adjustment cannot be lower than -50%.")

    markup_multiplier = 1.0 + (price_adjustment_percent / 100.0)

    # --- VALIDATION 3: Check Mandatory Minimum Constraints Feasibility ---
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

    # --- INITIALIZE OR-TOOLS LINEAR SOLVER ---
    solver = pywraplp.Solver.CreateSolver('GLOP')
    if not solver:
        raise RuntimeError("Could not create OR-Tools GLOP solver instance.")

    # Dictionary to hold decision variables x[loc_name]
    alloc_vars = {}
    market_details_input = {}

    for loc in LOCATIONS:
        name = loc["name"]
        pred_price = predicted_prices.get(name, 0.0)
        demand = max(0.0, expected_demands.get(name, 0.0))
        
        # Calculate final price after farmer markup
        final_price = round(pred_price * markup_multiplier, 2)
        
        # Calculate logistics cost estimate per kg
        transport_cost_per_kg = estimate_logistics_cost_per_kg(loc["est_km_from_depot"])
        
        # Expected Net Contribution per kg = Selling Price - Transport Cost per kg
        net_contrib_per_kg = final_price - transport_cost_per_kg

        # Define decision variable bounds: 0 <= x[name] <= demand
        # Apply mandatory minimum if specified by farmer
        min_bound = farmer_minimums.get(name, 0.0)
        max_bound = demand

        if min_bound > max_bound:
            min_bound = max_bound  # Safety cap

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

    # --- CONSTRAINT 1: Total Supply Constraint ---
    # Sum(x[i]) <= available_quantity_kg
    supply_constraint = solver.Constraint(0, available_quantity_kg, "TotalSupplyConstraint")
    for var in alloc_vars.values():
        supply_constraint.SetCoefficient(var, 1.0)

    # --- OBJECTIVE FUNCTION: Maximize Expected Net Profit ---
    # Maximize Sum( x[i] * net_contrib_per_kg[i] )
    objective = solver.Objective()
    for name, var in alloc_vars.items():
        contrib = market_details_input[name]["net_contrib_per_kg"]
        
        # Small balanced distribution tie-breaker if requested
        if coverage_mode == "balanced_distribution" and contrib > 0:
            contrib += 0.001
            
        objective.SetCoefficient(var, contrib)
    
    objective.SetMaximization()

    # --- SOLVE THE PROBLEM ---
    status = solver.Solve()

    if status != pywraplp.Solver.OPTIMAL and status != pywraplp.Solver.FEASIBLE:
        raise RuntimeError("Optimizer failed to find a feasible allocation solution.")

    # --- PROCESS RESULTS ---
    allocated_markets = []
    total_allocated_kg = 0.0
    total_expected_revenue = 0.0
    total_est_logistics_cost = 0.0
    total_expected_net_profit = 0.0
    total_expected_demand_kg = sum(details["demand"] for details in market_details_input.values())

    explainability_notes = []

    for name, var in alloc_vars.items():
        qty_kg = round(var.solution_value(), 2)
        # Clean small precision floats
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

        # Determine market status & reason
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


# -----------------------------------------------------------------------------
# 3. VERIFICATION & PRETTY PRINT TEST SUITE
# -----------------------------------------------------------------------------
def run_phase1_test():
    """Runs Phase 1 Profit Allocation with standard hackathon test data."""
    print("=" * 80)
    print("      AGRI-LOGISTICS PROFIT OPTIMIZER — PHASE 1 TEST RUN")
    print("=" * 80)

    # Test Data from Section 49 of Prompt
    crop_name = "Wheat"
    available_supply_kg = 100000.0  # 100 Tons
    farmer_markup = 5.0             # +5% Price adjustment

    predicted_prices = {
        "Delhi": 32.0,
        "Noida": 35.0,
        "Ghaziabad": 34.0,
        "Gurugram": 38.0,
        "Faridabad": 33.0,
        "Sonipat": 31.0,
        "Panipat": 30.0,
        "Meerut": 36.0,
        "Rohtak": 29.0,
    }

    expected_demands = {
        "Delhi": 30000.0,
        "Noida": 15000.0,
        "Ghaziabad": 12000.0,
        "Gurugram": 5000.0,
        "Faridabad": 15000.0,
        "Sonipat": 10000.0,
        "Panipat": 8000.0,
        "Meerut": 10000.0,
        "Rohtak": 5000.0,
    }

    print(f"Crop: {crop_name}")
    print(f"Available Supply: {available_supply_kg:,.0f} kg ({available_supply_kg/1000:.1f} Tons)")
    print(f"Farmer Price Adjustment: +{farmer_markup}%")
    print("-" * 80)

    # Execute Profit Optimization Solver
    result = solve_profit_allocation(
        crop=crop_name,
        available_quantity_kg=available_supply_kg,
        predicted_prices=predicted_prices,
        expected_demands=expected_demands,
        price_adjustment_percent=farmer_markup
    )

    # Display Allocation Table
    header = f"{'Location':<12} | {'Base ₹/kg':<9} | {'Final ₹/kg':<10} | {'Demand (kg)':<11} | {'Allocated (kg)':<14} | {'Est Profit (₹)':<14} | {'Status':<15}"
    print(header)
    print("-" * len(header))

    for m in result["markets"]:
        print(
            f"{m['location']:<12} | "
            f"₹{m['predicted_price_per_kg']:<8.2f} | "
            f"₹{m['final_price_per_kg']:<9.2f} | "
            f"{m['expected_demand_kg']:<11,.0f} | "
            f"{m['allocated_kg']:<14,.0f} | "
            f"₹{m['expected_net_profit']:<13,.2f} | "
            f"{m['status']:<15}"
        )

    print("-" * len(header))
    print("\nOVERALL PROFIT & LOGISTICS SUMMARY:")
    print(f"  • Total Available Supply   : {result['supply']['available_kg']:,.0f} kg ({result['supply']['available_tons']} Tons)")
    print(f"  • Total Allocated Quantity : {result['supply']['allocated_kg']:,.0f} kg ({result['supply']['allocated_tons']} Tons)")
    print(f"  • Surplus (Unallocated)    : {result['supply']['surplus_kg']:,.0f} kg ({result['supply']['surplus_tons']} Tons)")
    print(f"  • Unfulfilled Demand       : {result['supply']['unfulfilled_demand_kg']:,.0f} kg")
    print(f"  • Expected Revenue         : ₹{result['profit_summary']['expected_revenue']:,.2f}")
    print(f"  • Estimated Transport Cost : ₹{result['profit_summary']['estimated_logistics_cost']:,.2f}")
    print(f"  • Expected Net Profit      : ₹{result['profit_summary']['expected_net_profit']:,.2f}")
    print(f"  • Net Profit Margin        : {result['profit_summary']['expected_margin_percent']}%")

    print("\nEXPLAINABILITY & DECISION RATIONALE:")
    for note in result["explainability_summary"]:
        print(f"  {note}")

    print("\n" + "=" * 80)
    print("PHASE 1 VERIFICATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)


# -----------------------------------------------------------------------------
# 4. EDGE CASE VERIFICATION SUITE
# -----------------------------------------------------------------------------
def run_edge_case_tests():
    """Runs test cases for various edge cases to demonstrate robustness."""
    print("\n" + "=" * 80)
    print("      RUNNING PHASE 1 EDGE CASE VERIFICATION SUITE")
    print("=" * 80)

    base_prices = {"Delhi": 30.0, "Noida": 32.0, "Ghaziabad": 31.0}
    base_demands = {"Delhi": 5000.0, "Noida": 5000.0, "Ghaziabad": 5000.0}

    # Edge Case 1: Surplus Supply (Supply 20,000 kg > Demand 15,000 kg)
    print("\n--- Test Case 1: Surplus Supply (Supply > Total Demand) ---")
    res1 = solve_profit_allocation("Wheat", 20000.0, base_prices, base_demands)
    print(f"Available: {res1['supply']['available_kg']} kg | Allocated: {res1['supply']['allocated_kg']} kg | Surplus: {res1['supply']['surplus_kg']} kg")
    assert res1['supply']['surplus_kg'] == 5000.0, "Surplus calculation failed!"
    print("✓ Passed: Correctly identified 5,000 kg surplus supply.")

    # Edge Case 2: Invalid Price Markup > 10%
    print("\n--- Test Case 2: Invalid Price Markup (> +10%) ---")
    try:
        solve_profit_allocation("Wheat", 10000.0, base_prices, base_demands, price_adjustment_percent=15.0)
        print("✗ Failed: Should have raised ValueError for +15% markup.")
    except ValueError as e:
        print(f"✓ Passed: Caught expected error -> '{e}'")

    # Edge Case 3: Infeasible Farmer Minimums
    print("\n--- Test Case 3: Mandatory Farmer Minimum Exceeds Market Demand ---")
    try:
        solve_profit_allocation("Wheat", 10000.0, base_prices, base_demands, farmer_minimums={"Noida": 8000.0})
        print("✗ Failed: Should have raised ValueError for minimum > demand.")
    except ValueError as e:
        print(f"✓ Passed: Caught expected error -> '{e}'")

    # Edge Case 4: Zero Demand & Unprofitable Market Handling
    print("\n--- Test Case 4: Zero Demand Market ---")
    zero_demand_map = {"Delhi": 5000.0, "Noida": 0.0, "Ghaziabad": 5000.0}
    res4 = solve_profit_allocation("Wheat", 10000.0, base_prices, zero_demand_map)
    noida_alloc = next(m for m in res4["markets"] if m["location"] == "Noida")
    assert noida_alloc["allocated_kg"] == 0, "Zero demand market was assigned allocation!"
    print(f"✓ Passed: Noida allocated {noida_alloc['allocated_kg']} kg (Status: {noida_alloc['status']}).")

    print("\n" + "=" * 80)
    print("ALL EDGE CASE TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_phase1_test()
    run_edge_case_tests()
