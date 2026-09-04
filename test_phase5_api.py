"""
===============================================================================
PHASE 6 — FASTAPI ENDPOINTS AUTOMATED TEST SUITE
===============================================================================
File Path: test_phase5_api.py

Why this file exists:
---------------------
Tests all FastAPI endpoints using TestClient to verify API responses, JSON 
schemas, HTTP status codes, and edge-case error handling without requiring 
a running server.
===============================================================================
"""

import sys
import io
import json
from fastapi.testclient import TestClient
from backend.main import app

# Ensure UTF-8 output encoding for Windows PowerShell console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

client = TestClient(app)


def run_api_tests():
    print("=" * 85)
    print("      AGRI-LOGISTICS FASTAPI ENDPOINTS — PHASE 6 TEST RUN")
    print("=" * 85)

    # 1. Test GET /health
    print("1. Testing GET /health...")
    res_health = client.get("/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    print(f"   ✓ Status 200 OK: {res_health.json()}")

    # 2. Test GET /api/locations
    print("\n2. Testing GET /api/locations...")
    res_locs = client.get("/api/locations")
    assert res_locs.status_code == 200, f"Locations API failed: {res_locs.text}"
    loc_data = res_locs.json()
    assert len(loc_data) == 9, f"Expected 9 locations, got {len(loc_data)}"
    print(f"   ✓ Status 200 OK: Retrieved {len(loc_data)} Delhi-NCR locations (Depot: {loc_data[0]['name']})")

    # 3. Test POST /api/forecast
    print("\n3. Testing POST /api/forecast...")
    res_fc = client.post("/api/forecast", json={"crop": "Wheat", "date": "2026-09-02"})
    assert res_fc.status_code == 200, f"Forecast API failed: {res_fc.text}"
    fc_data = res_fc.json()
    print(f"   ✓ Status 200 OK: Crop={fc_data['crop']}, Markets Count={len(fc_data['markets'])}")

    # 4. Test POST /api/allocate
    print("\n4. Testing POST /api/allocate...")
    alloc_payload = {
        "crop": "Wheat",
        "date": "2026-09-02",
        "available_quantity_kg": 100000,
        "price_adjustment_percent": 5.0,
        "coverage_mode": "maximum_profit"
    }
    res_alloc = client.post("/api/allocate", json=alloc_payload)
    assert res_alloc.status_code == 200, f"Allocate API failed: {res_alloc.text}"
    alloc_data = res_alloc.json()
    print(f"   ✓ Status 200 OK: Allocated {alloc_data['supply']['allocated_kg']} kg | Est Profit: ₹{alloc_data['profit_summary']['expected_net_profit']:,}")

    # 5. Test POST /api/optimize-route
    print("\n5. Testing POST /api/optimize-route...")
    route_payload = {
        "crop": "Wheat",
        "allocations": {
            "Noida": 15000,
            "Ghaziabad": 12000,
            "Gurugram": 5000,
            "Faridabad": 15000,
            "Sonipat": 10000,
            "Panipat": 3000,
            "Meerut": 10000,
            "Rohtak": 0
        }
    }
    res_route = client.post("/api/optimize-route", json=route_payload)
    assert res_route.status_code == 200, f"Optimize-route API failed: {res_route.text}"
    route_data = res_route.json()
    print(f"   ✓ Status 200 OK: Dispatched {route_data['routing_summary']['vehicles_used']} trucks | Fleet Distance: {route_data['routing_summary']['total_distance_km']} km")

    # 6. Test Master Endpoint POST /api/optimize
    print("\n6. Testing Master End-to-End Orchestration POST /api/optimize...")
    master_payload = {
        "crop": "Wheat",
        "date": "2026-09-02",
        "available_quantity_kg": 100000,
        "price_adjustment_percent": 5.0,
        "coverage_mode": "maximum_profit"
    }
    res_master = client.post("/api/optimize", json=master_payload)
    assert res_master.status_code == 200, f"Master optimize API failed: {res_master.text}"
    m_data = res_master.json()
    print(f"   ✓ Status 200 OK: Master Orchestration Complete!")
    print(f"     • Total Allocated Supply  : {m_data['supply']['allocated_kg']} kg ({m_data['supply']['allocated_tons']} Tons)")
    print(f"     • Surplus Supply          : {m_data['supply']['surplus_kg']} kg")
    print(f"     • Final Expected Profit   : ₹{m_data['profit_summary']['expected_net_profit']:,} (Margin: {m_data['profit_summary']['expected_margin_percent']}%)")
    print(f"     • Trucks Used             : {m_data['routing_summary']['vehicles_used']} / {m_data['routing_summary']['vehicles_available']}")
    print(f"     • Fleet Total Distance    : {m_data['routing_summary']['total_distance_km']} km")

    # 7. Test Error Handling (Price Markup > 10%)
    print("\n7. Testing Validation Error Handling (+15% Markup)...")
    bad_payload = {"crop": "Wheat", "date": "2026-09-02", "available_quantity_kg": 100000, "price_adjustment_percent": 15.0}
    res_bad = client.post("/api/allocate", json=bad_payload)
    assert res_bad.status_code in (400, 422), f"Expected status 400 or 422, got {res_bad.status_code}"
    print(f"   ✓ Status {res_bad.status_code} Error: Caught expected validation error -> {res_bad.json()['detail']}")

    print("\n" + "=" * 85)
    print("ALL FASTAPI ENDPOINTS & EDGE CASES VERIFIED 100% SUCCESSFULLY!")
    print("=" * 85)


if __name__ == "__main__":
    run_api_tests()
