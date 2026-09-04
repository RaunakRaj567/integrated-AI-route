# backend/schemas/location.py
"""
Pydantic schemas for location data.
"""

from pydantic import BaseModel, Field
from typing import List


class LocationItem(BaseModel):
    id: int = Field(..., description="Unique integer ID")
    name: str = Field(..., description="Location/Hub name")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate")
    is_depot: bool = Field(False, description="True if central distribution warehouse")


class LocationsResponse(BaseModel):
    locations: List[LocationItem]
