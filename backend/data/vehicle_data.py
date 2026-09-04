"""
===============================================================================
VEHICLE FLEET DATA REPOSITORY
===============================================================================
File Path: backend/data/vehicle_data.py

Why this file exists:
---------------------
Centralizes vehicle fleet configuration and capacities (in kg).
Exactly 5 vehicles with increased capacities (20t, 22t, 25t, 28t, 30t = 125 Tons total)
to deliver large crop allocations efficiently.
===============================================================================
"""

# Exactly 5 vehicle capacities in kg (Total = 125 Tons capacity)
DEFAULT_VEHICLE_CAPACITIES = [
    20000,  # Vehicle 1 = 20 Tons (10t + 10t)
    22000,  # Vehicle 2 = 22 Tons (12t + 10t)
    25000,  # Vehicle 3 = 25 Tons (15t + 10t)
    28000,  # Vehicle 4 = 28 Tons (18t + 10t)
    30000   # Vehicle 5 = 30 Tons (20t + 10t)
]


def get_vehicle_fleet():
    colors = ["#2563eb", "#7c3aed", "#059669", "#ea580c", "#e11d48"]
    return [
        {
            "id": idx + 1,
            "name": f"Truck {idx + 1}",
            "capacity_kg": cap,
            "capacity_tons": cap / 1000.0,
            "color": colors[idx]
        }
        for idx, cap in enumerate(DEFAULT_VEHICLE_CAPACITIES)
    ]
