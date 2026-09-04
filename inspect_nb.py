import json

with open("Demand forecasting/wheat/wheat.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx, cell in enumerate(nb["cells"]):
    if cell["cell_type"] == "code":
        src = "".join(cell["source"])
        if "rolling_mean" in src or "lag_1" in src or "predict" in src:
            print(f"--- CELL {idx} ---")
            print(src[:600])
            print("...\n")
