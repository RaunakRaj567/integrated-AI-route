# backend/config.py
"""
Application Configuration
Contains URLs, default vehicle capacities, and CORS settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Server Settings
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

# CORS (Cross-Origin Resource Sharing)
# Allows the React frontend (running on http://localhost:5173 by default) to call this backend.
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
).split(",")

# OSRM Routing Endpoints
OSRM_TABLE_URL = os.getenv(
    "OSRM_TABLE_URL",
    "https://router.project-osrm.org/table/v1/driving/"
)
OSRM_ROUTE_URL = os.getenv(
    "OSRM_ROUTE_URL",
    "https://router.project-osrm.org/route/v1/driving/"
)

# Default Fleet Configuration (Capacities in kg)
DEFAULT_VEHICLE_CAPACITIES = [
    10000,  # Vehicle 1: 10 tons
    12000,  # Vehicle 2: 12 tons
    15000,  # Vehicle 3: 15 tons
    18000,  # Vehicle 4: 18 tons
    20000   # Vehicle 5: 20 tons
]
