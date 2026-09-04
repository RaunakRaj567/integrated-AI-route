"""
===============================================================================
DEBUG FORECAST MODEL SCRIPT
===============================================================================
"""
import os
import sys
import numpy as np
import pandas as pd
import sklearn.compose

if not hasattr(sklearn.compose.ColumnTransformer, "_name_to_fitted_passthrough"):
    setattr(sklearn.compose.ColumnTransformer, "_name_to_fitted_passthrough", {})

if not hasattr(np, "_core"):
    sys.modules["numpy._core"] = np.core
    sys.modules["numpy._core.multiarray"] = np.core.multiarray

import joblib

from backend.services.forecast_service import get_market_forecasts, get_loaded_model, build_feature_dataframe

def test_single_prediction():
    model = get_loaded_model("Wheat")
    print("Loaded model:", type(model))
    df = build_feature_dataframe("Wheat", "2026-09-02", "Noida", 35.0)
    print("DataFrame shape:", df.shape)
    print("Columns:", df.columns.tolist())
    try:
        pred = model.predict(df)
        print("Prediction SUCCESS:", pred)
    except Exception as e:
        print("Prediction EXCEPTION:", type(e), e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_prediction()
    prices, demands = get_market_forecasts("Wheat", "2026-09-02")
    print("Final Prices:", prices)
    print("Final Demands:", demands)
