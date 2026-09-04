from backend.services.allocation_service import run_allocation_service

for crop in ["Wheat", "Onion", "Rice"]:
    res = run_allocation_service(crop=crop, date="2026-09-02", available_quantity_kg=100000)
    print(f"=== {crop} ===")
    print(f"Allocated: {res['supply']['allocated_kg']} kg")
    print(f"Revenue: Rs. {res['profit_summary']['expected_revenue']:,}")
    print(f"Profit:  Rs. {res['profit_summary']['expected_net_profit']:,}")
