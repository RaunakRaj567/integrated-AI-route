"""
===============================================================================
ALLOCATION SERVICE MODULE
===============================================================================
File Path: backend/services/allocation_service.py

Why this file exists:
---------------------
Wraps Phase 1 profit optimization logic with input validation and forecast lookup.
===============================================================================
"""

from typing import Dict, Any, Optional
from backend.optimizer.profit_optimizer import solve_profit_allocation
from backend.services.forecast_service import get_market_forecasts


def run_allocation_service(
    crop: str,
    date: str,
    available_quantity_kg: float,
    price_adjustment_percent: float = 0.0,
    coverage_mode: str = "maximum_profit",
    farmer_minimums: Optional[Dict[str, float]] = None,
    predicted_prices: Optional[Dict[str, float]] = None,
    expected_demands: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Executes profit allocation service for FastAPI endpoints.
    """
    # 1. Fetch prices & demands if not provided in payload
    if not predicted_prices or not expected_demands:
        f_prices, f_demands = get_market_forecasts(crop, date)
        predicted_prices = predicted_prices or f_prices
        expected_demands = expected_demands or f_demands

    # 2. Execute Profit Allocation Solver
    return solve_profit_allocation(
        crop=crop,
        available_quantity_kg=available_quantity_kg,
        predicted_prices=predicted_prices,
        expected_demands=expected_demands,
        price_adjustment_percent=price_adjustment_percent,
        farmer_minimums=farmer_minimums,
        coverage_mode=coverage_mode
    )
