# backend/schemas/route.py
"""
Pydantic schemas for CVRP Route Optimization endpoints.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional


class OptimizeRouteRequest(BaseModel):
    crop: Optional[str] = Field("Wheat", description="Target crop")
    date: Optional[str] = Field("2026-09-02", description="Target delivery date")
    demands: Dict[str, float] = Field(
        ...,
        description="Dictionary mapping location name to demand in kg. e.g. {'Noida': 4200, 'Ghaziabad': 7100}"
    )
    vehicle_capacities: Optional[List[float]] = Field(
        None,
        description="Optional custom list of vehicle capacities in kg"
    )

    @field_validator("demands")
    @classmethod
    def validate_demands(cls, v):
        for loc, dem in v.items():
            if dem < 0:
                raise ValueError(f"Demand for {loc} cannot be negative ({dem} kg)")
        return v


class RouteItem(BaseModel):
    vehicle_id: int
    route_nodes: List[int]
    route: List[str]
    load_kg: float
    capacity_kg: float
    utilization_percent: float
    distance_km: float
    duration_minutes: float
    geometry: Optional[Dict[str, Any]] = None


class RouteSummary(BaseModel):
    total_demand_kg: float
    total_distance_km: float
    total_duration_minutes: float
    vehicles_used: int
    vehicles_available: int


class OptimizeRouteResponse(BaseModel):
    summary: RouteSummary
    routes: List[RouteItem]
    error: Optional[str] = None
