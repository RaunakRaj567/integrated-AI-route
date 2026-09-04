"""
===============================================================================
ROUTING PYDANTIC SCHEMAS
===============================================================================
File Path: backend/schemas/routing.py
===============================================================================
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from backend.schemas.allocation import SupplySummary, MarketAllocationItem, ProfitSummary

class RouteOptimizeRequest(BaseModel):
    crop: str
    allocations: Dict[str, float]  # e.g., {"Noida": 15000, "Ghaziabad": 12000, ...}
    vehicle_capacities: Optional[List[float]] = None

class GeoJSONGeometry(BaseModel):
    type: str = "LineString"
    coordinates: List[List[float]]

class VehicleRouteItem(BaseModel):
    vehicle_id: int
    vehicle_capacity_kg: float
    load_kg: float
    utilization_percent: float
    distance_km: float
    duration_minutes: float
    route_nodes: List[int]
    route_names: List[str]
    route_path_string: str
    geojson: Optional[GeoJSONGeometry] = None
    geojson_source: Optional[str] = "osrm_live"

class RoutingSummary(BaseModel):
    vehicles_available: int
    vehicles_used: int
    total_distance_km: float
    total_duration_minutes: float
    total_load_kg: float
    fleet_utilization_percent: float

class RoutingResponse(BaseModel):
    status: str
    routing_summary: RoutingSummary
    routes: List[VehicleRouteItem]

class MasterOptimizeRequest(BaseModel):
    crop: str = "Wheat"
    date: str = "2026-09-02"
    available_quantity_kg: float = 100000.0
    price_adjustment_percent: float = 5.0
    coverage_mode: str = "maximum_profit"
    farmer_minimums: Optional[Dict[str, float]] = None
    overrides: Optional[Dict[str, float]] = None

class MasterOptimizeResponse(BaseModel):
    crop: str
    date: str
    supply: SupplySummary
    markets: List[MarketAllocationItem]
    profit_summary: ProfitSummary
    routing_summary: RoutingSummary
    routes: List[VehicleRouteItem]
    explainability_summary: List[str]
