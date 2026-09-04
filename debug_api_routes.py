"""
===============================================================================
DEBUG API ROUTES SCRIPT
===============================================================================
"""
import json
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def debug_endpoints():
    print("=" * 80)
    print("      DEBUGGING FASTAPI API ROUTES")
    print("=" * 80)

    # 1. Test POST /api/allocate
    print("\n1. Testing POST /api/allocate...")
    alloc_payload = {
        "crop": "Wheat",
        "date": "2026-09-02",
        "available_quantity_kg": 100000.0,
        "price_adjustment_percent": 5.0,
        "coverage_mode": "maximum_profit"
    }
    r_alloc = client.post("/api/allocate", json=alloc_payload)
    print(f"Status: {r_alloc.status_code}")
    if r_alloc.status_code != 200:
        print("Error detail:", r_alloc.text)

    # 2. Test POST /api/optimize-route
    print("\n2. Testing POST /api/optimize-route...")
    route_payload = {
        "crop": "Wheat",
        "allocations": {
            "Noida": 15000.0,
            "Ghaziabad": 12000.0,
            "Gurugram": 5000.0,
            "Faridabad": 15000.0,
            "Sonipat": 10000.0,
            "Panipat": 8000.0,
            "Meerut": 10000.0,
            "Rohtak": 5000.0
        },
        "vehicle_capacities": [10000, 12000, 15000, 18000, 20000, 15000, 18000, 20000, 10000, 10000]
    }
    r_route = client.post("/api/optimize-route", json=route_payload)
    print(f"Status: {r_route.status_code}")
    if r_route.status_code != 200:
        print("Error detail:", r_route.text)
    else:
        res = r_route.json()
        print("Vehicles Used:", res["routing_summary"]["vehicles_used"])
        print("Total Distance:", res["routing_summary"]["total_distance_km"])

    # 3. Test POST /api/optimize (Master Orchestration)
    print("\n3. Testing POST /api/optimize...")
    master_payload = {
        "crop": "Wheat",
        "date": "2026-09-02",
        "available_quantity_kg": 100000.0,
        "price_adjustment_percent": 5.0,
        "coverage_mode": "maximum_profit",
        "overrides": {
            "Noida": 15000.0,
            "Ghaziabad": 12000.0,
            "Gurugram": 5000.0,
            "Faridabad": 15000.0,
            "Sonipat": 10000.0,
            "Panipat": 8000.0,
            "Meerut": 10000.0,
            "Rohtak": 5000.0
        }
    }
    r_master = client.post("/api/optimize", json=master_payload)
    print(f"Status: {r_master.status_code}")
    if r_master.status_code != 200:
        print("Error detail:", r_master.text)
    else:
        res = r_master.json()
        print("Allocated kg:", res["supply"]["allocated_kg"])
        print("Profit:", res["profit_summary"]["expected_net_profit"])
        print("Trucks Used:", res["routing_summary"]["vehicles_used"])

    print("\n" + "=" * 80)

if __name__ == "__main__":
    debug_endpoints()
