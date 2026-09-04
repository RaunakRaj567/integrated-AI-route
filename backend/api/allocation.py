"""
===============================================================================
FASTAPI ROUTER — ALLOCATION API
===============================================================================
File Path: backend/api/allocation.py
===============================================================================
"""

from fastapi import APIRouter, HTTPException
from backend.schemas.allocation import AllocationRequest, AllocationResponse
from backend.services.allocation_service import run_allocation_service

router = APIRouter(prefix="/api/allocate", tags=["Crop Allocation"])


@router.post("", response_model=AllocationResponse)
def allocate_crop(req: AllocationRequest):
    """
    Calculates profit-maximizing crop distribution among 8 Delhi-NCR markets.
    """
    try:
        res = run_allocation_service(
            crop=req.crop,
            date=req.date,
            available_quantity_kg=req.available_quantity_kg,
            price_adjustment_percent=req.price_adjustment_percent,
            coverage_mode=req.coverage_mode,
            farmer_minimums=req.farmer_minimums,
            predicted_prices=req.predicted_prices,
            expected_demands=req.expected_demands
        )
        return AllocationResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Allocation error: {str(e)}")
