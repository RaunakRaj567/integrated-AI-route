"""
===============================================================================
FORECAST PYDANTIC SCHEMAS
===============================================================================
File Path: backend/schemas/forecast.py
===============================================================================
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ForecastRequest(BaseModel):
    crop: str = Field(..., description="Crop name: Wheat, Onion, Rice, Maize")
    date: str = Field(..., description="Prediction date YYYY-MM-DD")

class MarketForecastItem(BaseModel):
    location: str
    predicted_price_per_kg: float
    expected_demand_kg: float

class ForecastResponse(BaseModel):
    crop: str
    date: str
    markets: List[MarketForecastItem]
