# backend/schemas/demand.py
"""
Pydantic schemas for Demand Forecasting.
"""

from pydantic import BaseModel, Field
from typing import List


class ForecastRequest(BaseModel):
    crop: str = Field("Wheat", description="Agricultural crop type (Wheat, Rice, Mustard, Potato)")
    date: str = Field("2026-09-02", description="Forecast target date (YYYY-MM-DD)")


class PredictionItem(BaseModel):
    location: str
    demand_kg: float = Field(..., ge=0.0, description="Predicted demand in kilograms")


class ForecastResponse(BaseModel):
    crop: str
    date: str
    predictions: List[PredictionItem]
