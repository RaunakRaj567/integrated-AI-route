"""
===============================================================================
ML MODEL INSPECTION SCRIPT
===============================================================================
File Path: test_ml_models.py

Why this file exists:
---------------------
Loads and inspects the user's pre-trained .joblib forecasting models from the 
'Demand forecasting/' directory to determine input feature requirements.
===============================================================================
"""

import os
import sys
import numpy as np

# Compatibility alias for unpickling models created with NumPy 2.0+ on NumPy 1.x
if not hasattr(np, "_core"):
    sys.modules["numpy._core"] = np.core
    sys.modules["numpy._core.multiarray"] = np.core.multiarray

import joblib

MODEL_PATHS = {
    "Wheat": "Demand forecasting/wheat/wheat_demand_forecasting_model.joblib",
    "Onion": "Demand forecasting/Onion/linear_regression_demand_model_onion.joblib",
    "Rice": "Demand forecasting/riceee/rice_demand_forecasting_model.joblib"
}

def inspect_models():
    print("=" * 80)
    print("      INSPECTING USER PRE-TRAINED DEMAND FORECASTING MODELS")
    print("=" * 80)

    for crop, path in MODEL_PATHS.items():
        if os.path.exists(path):
            try:
                model = joblib.load(path)
                print(f"\n[CROP: {crop}]")
                print(f"  • File Path : {path}")
                print(f"  • Model Type: {type(model)}")
                if hasattr(model, "feature_names_in_"):
                    print(f"  • Feature Names: {model.feature_names_in_}")
                if hasattr(model, "n_features_in_"):
                    print(f"  • Feature Count: {model.n_features_in_}")
            except Exception as e:
                print(f"  • Error loading {path}: {e}")
        else:
            print(f"\n[CROP: {crop}] File not found at '{path}'")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    inspect_models()
