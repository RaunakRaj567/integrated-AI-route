# backend/data/sample_demands.py
"""
Sample agricultural demand predictions by crop and date.
Used as baseline/mock prior to loading custom ML .joblib models.
"""

SAMPLE_DEMANDS = {
    "Wheat": {
        "Noida": 4200,
        "Ghaziabad": 7100,
        "Gurugram": 0,
        "Faridabad": 5100,
        "Sonipat": 3000,
        "Panipat": 8000,
        "Meerut": 0,
        "Rohtak": 6000
    },
    "Rice": {
        "Noida": 5500,
        "Ghaziabad": 6200,
        "Gurugram": 4000,
        "Faridabad": 3500,
        "Sonipat": 4800,
        "Panipat": 7200,
        "Meerut": 3100,
        "Rohtak": 4500
    },
    "Mustard": {
        "Noida": 2200,
        "Ghaziabad": 3100,
        "Gurugram": 1800,
        "Faridabad": 2900,
        "Sonipat": 1500,
        "Panipat": 2000,
        "Meerut": 1200,
        "Rohtak": 3800
    },
    "Potato": {
        "Noida": 8000,
        "Ghaziabad": 9500,
        "Gurugram": 7200,
        "Faridabad": 6800,
        "Sonipat": 5000,
        "Panipat": 8500,
        "Meerut": 6200,
        "Rohtak": 7000
    }
}


def get_sample_demand(crop: str = "Wheat"):
    return SAMPLE_DEMANDS.get(crop, SAMPLE_DEMANDS["Wheat"])
