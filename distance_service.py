# distance_service.py

import requests

from locations import get_coordinates


OSRM_TABLE_URL = (
    "https://router.project-osrm.org/table/v1/driving/"
)


def get_road_matrix():

    coordinates = get_coordinates()

    coordinate_string = ";".join(
        f"{lon},{lat}"
        for lon, lat in coordinates
    )

    url = (
        OSRM_TABLE_URL
        + coordinate_string
    )

    params = {
        "annotations": "distance,duration"
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
            f"OSRM error: {data.get('code')}"
        )

    distance_matrix = data["distances"]

    duration_matrix = data["durations"]

    # Convert meters → kilometers
    distance_matrix_km = []

    for row in distance_matrix:

        converted_row = []

        for value in row:

            if value is None:
                converted_row.append(None)
            else:
                converted_row.append(
                    round(value / 1000, 2)
                )

        distance_matrix_km.append(
            converted_row
        )

    # Convert seconds → minutes
    duration_matrix_min = []

    for row in duration_matrix:

        converted_row = []

        for value in row:

            if value is None:
                converted_row.append(None)
            else:
                converted_row.append(
                    round(value / 60, 2)
                )

        duration_matrix_min.append(
            converted_row
        )

    return (
        distance_matrix_km,
        duration_matrix_min
    )


if __name__ == "__main__":

    distances, durations = get_road_matrix()

    print("\nROAD DISTANCE MATRIX (km)")
    print("=" * 60)

    for row in distances:
        print(row)

    print("\nTRAVEL TIME MATRIX (minutes)")
    print("=" * 60)

    for row in durations:
        print(row)