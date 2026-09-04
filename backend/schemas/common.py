"""
===============================================================================
COMMON PYDANTIC SCHEMAS
===============================================================================
File Path: backend/schemas/common.py
===============================================================================
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class LocationSchema(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    is_depot: bool

class HealthResponse(BaseModel):
    status: str
    service: str
