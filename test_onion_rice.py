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

for crop, path, data_path in [
    ("Onion", "Demand forecasting/Onion/linear_regression_demand_model_onion.joblib", "Demand forecasting/Onion/onionn_market_1000.xls"),
    ("Rice", "Demand forecasting/riceee/rice_demand_forecasting_model.joblib", "Demand forecasting/riceee/rice_market_1000.xls")
]:
    df = pd.read_csv(data_path)
    model = joblib.load(path)
    print(crop, "Data shape:", df.shape, "Model:", type(model))
