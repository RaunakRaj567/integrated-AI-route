# backend/api/demand.py
"""
Demand Forecasting API Router.
"""

from fastapi import APIRouter
from schemas.demand import ForecastRequest, ForecastResponse, PredictionItem
from services.demand_service import predict_demand

router = APIRouter(prefix="", tags=["Demand Forecasting"])


@router.post("/forecast", response_model=ForecastResponse)
def get_forecast(payload: ForecastRequest):
    """
    Generates location-wise demand predictions for the requested crop and date.
    """
    predictions_dict = predict_demand(crop=payload.crop, date_str=payload.date)
    
    prediction_items = [
        PredictionItem(location=loc_name, demand_kg=demand)
        for loc_name, demand in predictions_dict.items()
    ]

    return ForecastResponse(
        crop=payload.crop,
        date=payload.date,
        predictions=prediction_items
    )
