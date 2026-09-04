# route_geometry.py

import requests

from locations import LOCATIONS


OSRM_ROUTE_URL = (
    "https://router.project-osrm.org/route/v1/driving/"
)


def get_route_geometry(route_nodes):

    coordinates = []

    for node in route_nodes:

        location = LOCATIONS[node]

        coordinates.append(
            (
                location["longitude"],
                location["latitude"]
            )
        )

    coordinate_string = ";".join(
        f"{lon},{lat}"
        for lon, lat in coordinates
    )

    url = (
        OSRM_ROUTE_URL
        + coordinate_string
    )

    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "false"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok":

        raise RuntimeError(
            f"OSRM route error: "
            f"{data.get('code')}"
        )

    route = data["routes"][0]

    return {
        "distance_km":
            round(
                route["distance"] / 1000,
                2
            ),

        "duration_minutes":
            round(
                route["duration"] / 60,
                2
            ),

        "geometry":
            route["geometry"]
    }