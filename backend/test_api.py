"""
===============================================================================
BACKEND UNIT TEST SUITE (FASTAPI TESTCLIENT)
===============================================================================
File Path: backend/test_api.py
===============================================================================
"""

import sys
import os

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_locations():
    response = client.get("/api/locations")
    assert response.status_code == 200
    assert len(response.json()) == 9

def test_forecast():
    response = client.post("/api/forecast", json={"crop": "Wheat", "date": "2026-09-02"})
    assert response.status_code == 200
    assert response.json()["crop"] == "Wheat"

def test_allocate():
    response = client.post("/api/allocate", json={
        "crop": "Wheat",
        "date": "2026-09-02",
        "available_quantity_kg": 100000,
        "price_adjustment_percent": 5.0
    })
    assert response.status_code == 200
    assert response.json()["supply"]["allocated_kg"] > 0

def test_optimize():
    response = client.post("/api/optimize", json={
        "crop": "Wheat",
        "date": "2026-09-02",
        "available_quantity_kg": 100000,
        "price_adjustment_percent": 5.0
    })
    assert response.status_code == 200
    assert len(response.json()["routes"]) > 0

if __name__ == "__main__":
    test_health()
    test_locations()
    test_forecast()
    test_allocate()
    test_optimize()
    print("All backend unit tests passed 100% successfully!")
