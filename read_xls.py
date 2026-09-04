"""
===============================================================================
INSPECT EXCEL & PREDICTIONS SCRIPT
===============================================================================
"""
import pandas as pd
import os

files = [
    "Demand forecasting/wheat/predicted_wheat_demand_for_routing.xls",
    "Demand forecasting/Onion/predicted_onion_demand_for_routing.xls",
    "Demand forecasting/riceee/predicted_rice_demand_for_routing.xls"
]

for f in files:
    if os.path.exists(f):
        print("File:", f)
        try:
            df = pd.read_excel(f) if f.endswith(".xls") else pd.read_csv(f)
            print(df.head(10))
        except Exception as e:
            print("Error reading:", e)
    else:
        print("Missing:", f)
