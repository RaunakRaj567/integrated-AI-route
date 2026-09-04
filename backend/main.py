"""
===============================================================================
FASTAPI MAIN APPLICATION ENTRYPOINT
===============================================================================
File Path: backend/main.py

Why this file exists:
---------------------
Initializes FastAPI application instance, configures CORS middleware for React 
frontend integration, mounts routers, and defines root/health endpoints.
===============================================================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.locations import router as locations_router
from backend.api.forecast import router as forecast_router
from backend.api.allocation import router as allocation_router
from backend.api.routes import router as routes_router

app = FastAPI(
    title="Agri-Logistics Optimization Portal API",
    description="AI-Powered Agricultural Profit Optimization & CVRP Vehicle Routing Engine",
    version="1.0.0"
)

# Configure CORS Middleware for React frontend (Vite default port 5173 / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for hackathon development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(locations_router)
app.include_router(forecast_router)
app.include_router(allocation_router)
app.include_router(routes_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Agri-Logistics Optimization Portal API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
