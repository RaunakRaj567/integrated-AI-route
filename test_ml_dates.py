import os
import sys
import pandas as pd
import numpy as np
import sklearn.compose
import joblib

if not hasattr(sklearn.compose.ColumnTransformer, "_name_to_fitted_passthrough"):
    setattr(sklearn.compose.ColumnTransformer, "_name_to_fitted_passthrough", {})

if not hasattr(np, "_core"):
    sys.modules["numpy._core"] = np.core
    sys.modules["numpy._core.multiarray"] = np.core.multiarray

df_wheat = pd.read_csv("Demand forecasting/wheat/wheat_market_1000.xls")
model_wheat = joblib.load("Demand forecasting/wheat/wheat_demand_forecasting_model.joblib")

feature_columns = [
    "location", "crop", "price_per_kg", "temperature_c", "rainfall_mm", "market_arrivals_kg", "festival_flag",
    "year", "month", "day", "day_of_week", "day_of_year", "week_of_year", "quarter", "is_weekend",
    "month_sin", "month_cos", "day_of_week_sin", "day_of_week_cos",
    "lag_1", "lag_2", "lag_3", "lag_7", "lag_14", "lag_30",
    "rolling_mean_7", "rolling_mean_14", "rolling_mean_30", "rolling_std_7", "rolling_std_30"
]

def predict_wheat_for_date(future_date_str):
    preds = {}
    for loc in ["Delhi", "Noida", "Ghaziabad", "Gurugram", "Faridabad", "Sonipat", "Panipat", "Meerut", "Rohtak"]:
        history = df_wheat[(df_wheat["location"] == loc) & (df_wheat["crop"] == "Wheat")].sort_values("date")
        demand_history = history["demand_kg"].values
        latest = history.iloc[-1]
        
        dt = pd.to_datetime(future_date_str)
        week_num = int(dt.isocalendar()[1])
        row = {
            "location": loc, "crop": "Wheat",
            "price_per_kg": float(latest["price_per_kg"]),
            "temperature_c": float(latest["temperature_c"]),
            "rainfall_mm": float(latest["rainfall_mm"]),
            "market_arrivals_kg": int(latest["market_arrivals_kg"]),
            "festival_flag": 1 if dt.month in [10, 11] else 0,
            "year": dt.year, "month": dt.month, "day": dt.day,
            "day_of_week": dt.dayofweek, "day_of_year": dt.dayofyear,
            "week_of_year": week_num, "quarter": dt.quarter,
            "is_weekend": int(dt.dayofweek >= 5),
            "month_sin": np.sin(2 * np.pi * dt.month / 12),
            "month_cos": np.cos(2 * np.pi * dt.month / 12),
            "day_of_week_sin": np.sin(2 * np.pi * dt.dayofweek / 7),
            "day_of_week_cos": np.cos(2 * np.pi * dt.dayofweek / 7),
        }
        for lag in [1, 2, 3, 7, 14, 30]:
            row[f"lag_{lag}"] = demand_history[-lag]
        row["rolling_mean_7"] = np.mean(demand_history[-7:])
        row["rolling_mean_14"] = np.mean(demand_history[-14:])
        row["rolling_mean_30"] = np.mean(demand_history[-30:])
        row["rolling_std_7"] = np.std(demand_history[-7:], ddof=1)
        row["rolling_std_30"] = np.std(demand_history[-30:], ddof=1)
        
        df_row = pd.DataFrame([row])[feature_columns]
        pred = model_wheat.predict(df_row)[0]
        preds[loc] = round(float(pred), 2)
    return preds

print("\nPredictions for 2026-09-02:")
print(predict_wheat_for_date("2026-09-02"))

print("\nPredictions for 2026-11-15 (Diwali/Festival Season):")
print(predict_wheat_for_date("2026-11-15"))

print("\nPredictions for 2026-05-20 (Summer Season):")
print(predict_wheat_for_date("2026-05-20"))
