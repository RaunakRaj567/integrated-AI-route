"""
===============================================================================
CENTRALIZED LOCATION DATA STORE (BACKEND MODULE)
===============================================================================
File Path: backend/data/locations.py

Why this file exists:
---------------------
Provides location dictionary and helper getters for FastAPI endpoints and services.
===============================================================================
"""

LOCATIONS = [
    {"id": 0, "name": "Delhi",     "latitude": 28.6139, "longitude": 77.2090, "is_depot": True},
    {"id": 1, "name": "Noida",     "latitude": 28.5355, "longitude": 77.3910, "is_depot": False},
    {"id": 2, "name": "Ghaziabad", "latitude": 28.6692, "longitude": 77.4538, "is_depot": False},
    {"id": 3, "name": "Gurugram",  "latitude": 28.4595, "longitude": 77.0266, "is_depot": False},
    {"id": 4, "name": "Faridabad", "latitude": 28.4089, "longitude": 77.3178, "is_depot": False},
    {"id": 5, "name": "Sonipat",   "latitude": 28.9931, "longitude": 77.0151, "is_depot": False},
    {"id": 6, "name": "Panipat",   "latitude": 29.3909, "longitude": 76.9635, "is_depot": False},
    {"id": 7, "name": "Meerut",    "latitude": 28.9845, "longitude": 77.7064, "is_depot": False},
    {"id": 8, "name": "Rohtak",    "latitude": 28.8955, "longitude": 76.6066, "is_depot": False},
]

def get_locations():
    return LOCATIONS

def get_coordinates():
    return [(loc["longitude"], loc["latitude"]) for loc in LOCATIONS]

def get_location_names():
    return [loc["name"] for loc in LOCATIONS]
