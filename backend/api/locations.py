"""
===============================================================================
FASTAPI ROUTER — LOCATIONS API
===============================================================================
File Path: backend/api/locations.py
===============================================================================
"""

from fastapi import APIRouter
from typing import List
from backend.data.locations import LOCATIONS
from backend.schemas.common import LocationSchema

router = APIRouter(prefix="/api/locations", tags=["Locations"])


@router.get("", response_model=List[LocationSchema])
def get_all_locations():
    """Returns central 9 Delhi-NCR locations metadata."""
    return LOCATIONS
