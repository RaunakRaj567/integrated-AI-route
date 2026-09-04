"""
===============================================================================
OSRM ROAD GEOMETRY SERVICE (GeoJSON LINESTRING)
===============================================================================
File Path: backend/services/geometry_service.py

Why this file exists:
---------------------
Obtains exact GeoJSON LineString road geometry for each vehicle's stop sequence
from OSRM Route Service, to enable seamless rendering on React-Leaflet maps.
===============================================================================
"""

import requests
from typing import List, Dict, Any
from backend.data.locations import LOCATIONS

OSRM_ROUTE_URL = "https://router.project-osrm.org/route/v1/driving/"


def get_fallback_geometry(route_nodes: List[int]) -> Dict[str, Any]:
    """Generates straight-line GeoJSON geometry if OSRM is offline."""
    coordinates = [
        [LOCATIONS[node]["longitude"], LOCATIONS[node]["latitude"]]
        for node in route_nodes
    ]
    return {
        "type": "LineString",
        "coordinates": coordinates
    }


def get_route_geometry(route_nodes: List[int], timeout_seconds: int = 5) -> Dict[str, Any]:
    """
    Fetches real road geometry (GeoJSON LineString) from OSRM Route API.

    Parameters:
      route_nodes: List of location indices e.g. [0, 1, 2, 0] (Delhi -> Noida -> Ghaziabad -> Delhi)

    Returns:
      Dict with GeoJSON geometry, distance_km, and duration_minutes.
    """
    if len(route_nodes) < 2:
        return {
            "distance_km": 0.0,
            "duration_minutes": 0.0,
            "geometry": get_fallback_geometry(route_nodes),
            "source": "fallback_empty"
        }

    coords = [
        f"{LOCATIONS[node]['longitude']},{LOCATIONS[node]['latitude']}"
        for node in route_nodes
    ]
    coord_str = ";".join(coords)
    url = f"{OSRM_ROUTE_URL}{coord_str}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "false"
    }

    try:
        response = requests.get(url, params=params, timeout=timeout_seconds)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            raise RuntimeError(f"OSRM Route Error: {data.get('code')}")

        route = data["routes"][0]
        return {
            "distance_km": round(route["distance"] / 1000.0, 2),
            "duration_minutes": round(route["duration"] / 60.0, 1),
            "geometry": route["geometry"],
            "source": "osrm_live"
        }

    except Exception as e:
        print(f"[WARNING] OSRM Route Geometry API unavailable ({e}). Using straight-line GeoJSON geometry.")
        return {
            "distance_km": 0.0,
            "duration_minutes": 0.0,
            "geometry": get_fallback_geometry(route_nodes),
            "source": "fallback_straight_line"
        }
