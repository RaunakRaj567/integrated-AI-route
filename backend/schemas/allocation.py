"""
===============================================================================
ALLOCATION PYDANTIC SCHEMAS
===============================================================================
File Path: backend/schemas/allocation.py
===============================================================================
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class AllocationRequest(BaseModel):
    crop: str
    date: str
    available_quantity_kg: float = Field(..., gt=0)
    price_adjustment_percent: float = Field(default=0.0, ge=-50.0, le=10.0)
    coverage_mode: str = "maximum_profit"
    farmer_minimums: Optional[Dict[str, float]] = None
    predicted_prices: Optional[Dict[str, float]] = None
    expected_demands: Optional[Dict[str, float]] = None

class MarketAllocationItem(BaseModel):
    location: str
    is_depot: bool
    latitude: float
    longitude: float
    predicted_price_per_kg: float
    final_price_per_kg: float
    expected_demand_kg: float
    allocated_kg: float
    allocated_tons: float
    est_transport_cost_per_kg: float
    expected_net_contrib_per_kg: float
    expected_revenue: float
    estimated_logistics_cost: float
    expected_net_profit: float
    unfulfilled_demand_kg: float
    status: str
    explainability: str

class SupplySummary(BaseModel):
    available_kg: float
    available_tons: float
    allocated_kg: float
    allocated_tons: float
    surplus_kg: float
    surplus_tons: float
    total_expected_demand_kg: float
    unfulfilled_demand_kg: float

class ProfitSummary(BaseModel):
    expected_revenue: float
    estimated_logistics_cost: float
    expected_net_profit: float
    expected_margin_percent: float

class AllocationResponse(BaseModel):
    crop: str
    status: str
    price_adjustment_percent: float
    coverage_mode: str
    supply: SupplySummary
    profit_summary: ProfitSummary
    markets: List[MarketAllocationItem]
    explainability_summary: List[str]
