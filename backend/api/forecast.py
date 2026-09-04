"""
===============================================================================
FASTAPI ROUTER — FORECAST API
===============================================================================
File Path: backend/api/forecast.py
===============================================================================
"""

from fastapi import APIRouter, HTTPException
from backend.schemas.forecast import ForecastRequest, ForecastResponse, MarketForecastItem
from backend.services.forecast_service import get_market_forecasts

router = APIRouter(prefix="/api/forecast", tags=["Forecasting"])


@router.post("", response_model=ForecastResponse)
def get_forecast(req: ForecastRequest):
    """
    Returns location-wise price & demand predictions for a specified crop and date.
    """
    try:
        prices, demands = get_market_forecasts(req.crop, req.date)
        items = [
            MarketForecastItem(
                location=loc,
                predicted_price_per_kg=prices[loc],
                expected_demand_kg=demands[loc]
            )
            for loc in prices
        ]
        return ForecastResponse(crop=req.crop, date=req.date, markets=items)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting error: {str(e)}")
