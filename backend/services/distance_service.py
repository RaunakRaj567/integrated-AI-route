"""
===============================================================================
OSRM ROAD DISTANCE & TIME MATRIX SERVICE
===============================================================================
File Path: backend/services/distance_service.py

Why this file exists:
---------------------
Fetches real road distance (km) and travel duration (minutes) matrices for all 
9 Delhi-NCR coordinates using OSRM Table Service. Includes robust Haversine 
fallback handling if OSRM is offline or times out.
===============================================================================
"""

import math
import requests
from typing import Tuple, List
from backend.data.locations import get_coordinates, LOCATIONS

OSRM_TABLE_URL = "https://router.project-osrm.org/table/v1/driving/"


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c * 1.3, 2)


def get_fallback_road_matrix() -> Tuple[List[List[float]], List[List[float]]]:
    """Generates estimated distance and duration matrix when OSRM API is unavailable."""
    num_locs = len(LOCATIONS)
    dist_matrix = [[0.0] * num_locs for _ in range(num_locs)]
    dur_matrix = [[0.0] * num_locs for _ in range(num_locs)]

    for i in range(num_locs):
        for j in range(num_locs):
            if i != j:
                d_km = haversine_distance_km(
                    LOCATIONS[i]["latitude"], LOCATIONS[i]["longitude"],
                    LOCATIONS[j]["latitude"], LOCATIONS[j]["longitude"]
                )
                dist_matrix[i][j] = d_km
                # Estimate 40 km/h average speed in NCR traffic
                dur_matrix[i][j] = round((d_km / 40.0) * 60.0, 1)

    return dist_matrix, dur_matrix


def get_road_matrix(timeout_seconds: int = 5) -> Tuple[List[List[float]], List[List[float]], str]:
    """
    Fetches road distance (km) and travel time (mins) matrices from OSRM Table Service.

    Returns:
      (distance_matrix_km, duration_matrix_minutes, source_flag)
    """
    coords = get_coordinates()
    coord_str = ";".join(f"{lon},{lat}" for lon, lat in coords)
    url = f"{OSRM_TABLE_URL}{coord_str}"
    params = {"annotations": "distance,duration"}

    try:
        response = requests.get(url, params=params, timeout=timeout_seconds)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "Ok":
            raise RuntimeError(f"OSRM Error Code: {data.get('code')}")

        raw_distances = data["distances"]
        raw_durations = data["durations"]

        distance_km = [
            [round(val / 1000.0, 2) if val is not None else 0.0 for val in row]
            for row in raw_distances
        ]

        duration_mins = [
            [round(val / 60.0, 1) if val is not None else 0.0 for val in row]
            for row in raw_durations
        ]

        return distance_km, duration_mins, "osrm_live"

    except Exception as e:
        print(f"[WARNING] OSRM Matrix API unavailable or timed out ({e}). Using Haversine road matrix fallback.")
        dist_fb, dur_fb = get_fallback_road_matrix()
        return dist_fb, dur_fb, "haversine_fallback"
