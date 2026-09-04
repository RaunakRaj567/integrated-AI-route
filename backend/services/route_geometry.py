# backend/services/route_geometry.py
"""
Service to fetch exact road geometries (GeoJSON) from OSRM Route API.
"""

import requests
from config import OSRM_ROUTE_URL
from data.locations import LOCATIONS


def get_route_geometry(route_nodes, custom_locations=None):
    """
    Given an ordered list of node indices (e.g. [0, 1, 5, 0]), calls OSRM Route API
    to get the exact road trajectory in GeoJSON format.
    
    Parameters:
    - route_nodes (list of int): List of node IDs in sequence.
    - custom_locations (list of dict, optional): Full location objects list.
    
    Returns:
    - dict: {"distance_km": float, "duration_minutes": float, "geometry": dict}
    """
    loc_pool = custom_locations if custom_locations is not None else LOCATIONS

    coordinates = []
    for node in route_nodes:
        loc = loc_pool[node]
        coordinates.append((loc["longitude"], loc["latitude"]))

    coordinate_string = ";".join(f"{lon},{lat}" for lon, lat in coordinates)
    url = f"{OSRM_ROUTE_URL}{coordinate_string}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "false"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch route geometry from OSRM: {e}")

    if data.get("code") != "Ok":
        raise RuntimeError(f"OSRM Route error: {data.get('code')}")

    route = data["routes"][0]
    return {
        "distance_km": round(route["distance"] / 1000.0, 2),
        "duration_minutes": round(route["duration"] / 60.0, 2),
        "geometry": route["geometry"]
    }
