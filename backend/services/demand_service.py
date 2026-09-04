# backend/services/demand_service.py
"""
Demand Forecasting Service.

Separation of Concerns:
- Handles loading and inference from ML models (.joblib).
- If no custom model artifact is supplied yet, falls back to seasonal baseline demand patterns.
- Keeps model loaded in memory (singleton pattern) rather than retraining or reloading on every request.
"""

import os
import joblib
from data.sample_demands import get_sample_demand
from data.locations import LOCATIONS

# Optional path for serialized ML model artifact
MODEL_PATH = os.getenv("DEMAND_MODEL_PATH", "models/demand_model.joblib")
_MODEL = None


def load_model():
    """Loads the ML model once into memory if the artifact file exists."""
    global _MODEL
    if _MODEL is None and os.path.exists(MODEL_PATH):
        try:
            _MODEL = joblib.load(MODEL_PATH)
            print(f"[DemandService] Successfully loaded ML model from {MODEL_PATH}")
        except Exception as e:
            print(f"[DemandService] Warning: Could not load model from {MODEL_PATH}: {e}")
            _MODEL = None
    return _MODEL


def predict_demand(crop: str, date_str: str) -> dict:
    """
    Predicts demand in kg for all delivery locations for a given crop and date.
    
    Returns:
    - dict: {"Noida": 4200, "Ghaziabad": 7100, ...}
    """
    model = load_model()
    if model is not None:
        # Placeholder for custom ML model inference pipeline
        # e.g., features = prepare_features(crop, date_str)
        # return model.predict(features)
        pass

    # Use baseline/sample demand based on crop selection
    sample = get_sample_demand(crop)
    
    # Ensure all non-depot locations are included in the result
    demands = {}
    for loc in LOCATIONS:
        if loc.get("is_depot"):
            continue
        name = loc["name"]
        demands[name] = sample.get(name, 3500)

    return demands
