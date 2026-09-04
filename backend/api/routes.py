"""
===============================================================================
FASTAPI ROUTER — ROUTE OPTIMIZATION & MASTER ORCHESTRATION API
===============================================================================
File Path: backend/api/routes.py
===============================================================================
"""

from fastapi import APIRouter, HTTPException
from backend.schemas.routing import (
    RouteOptimizeRequest, RoutingResponse,
    MasterOptimizeRequest, MasterOptimizeResponse
)
from backend.services.routing_service import run_routing_service
from backend.services.allocation_service import run_allocation_service

router = APIRouter(tags=["Route Optimization & Orchestration"])


@router.post("/api/optimize-route", response_model=RoutingResponse)
def optimize_vehicle_routes(req: RouteOptimizeRequest):
    """
    Solves CVRP vehicle routing for given market allocations.
    """
    try:
        res = run_routing_service(
            allocations_map=req.allocations,
            vehicle_capacities=req.vehicle_capacities
        )
        return RoutingResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing error: {str(e)}")


@router.post("/api/optimize", response_model=MasterOptimizeResponse)
def master_optimize(req: MasterOptimizeRequest):
    """
    Master end-to-end orchestration endpoint:
    Forecast -> Allocation -> Farmer Overrides -> CVRP -> OSRM Road Geometry -> Response.
    """
    try:
        # 1. Solve Crop Allocation
        alloc_res = run_allocation_service(
            crop=req.crop,
            date=req.date,
            available_quantity_kg=req.available_quantity_kg,
            price_adjustment_percent=req.price_adjustment_percent,
            coverage_mode=req.coverage_mode,
            farmer_minimums=req.farmer_minimums
        )

        # 2. Apply Farmer Overrides if provided
        alloc_map = {m["location"]: m["allocated_kg"] for m in alloc_res["markets"]}
        if req.overrides:
            for loc, manual_qty in req.overrides.items():
                if loc in alloc_map:
                    alloc_map[loc] = max(0.0, manual_qty)

        # 3. Solve CVRP Routing & Geometry
        routing_res = run_routing_service(allocations_map=alloc_map)

        # 4. Final Financial Summary Calculation
        cost_per_truck_km = 100.0
        actual_transport_cost = round(routing_res["routing_summary"]["total_distance_km"] * cost_per_truck_km, 2)
        expected_revenue = alloc_res["profit_summary"]["expected_revenue"]
        final_profit = round(expected_revenue - actual_transport_cost, 2)
        final_margin = round((final_profit / expected_revenue * 100.0), 2) if expected_revenue > 0 else 0.0

        profit_summary = {
            "expected_revenue": expected_revenue,
            "estimated_logistics_cost": actual_transport_cost,
            "expected_net_profit": final_profit,
            "expected_margin_percent": final_margin
        }

        return MasterOptimizeResponse(
            crop=req.crop,
            date=req.date,
            supply=alloc_res["supply"],
            markets=alloc_res["markets"],
            profit_summary=profit_summary,
            routing_summary=routing_res["routing_summary"],
            routes=routing_res["routes"],
            explainability_summary=alloc_res["explainability_summary"]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Master optimization error: {str(e)}")
