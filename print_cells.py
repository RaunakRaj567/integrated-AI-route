import json

with open("Demand forecasting/wheat/wheat.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print("=== CELL 65 ===")
print("".join(nb["cells"][65]["source"]))

print("\n=== CELL 68 ===")
print("".join(nb["cells"][68]["source"]))
