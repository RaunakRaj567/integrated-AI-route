// frontend/src/services/api.js
/**
 * Centralized API Service for communicating with FastAPI backend.
 * Includes automatic dual-origin fallback (127.0.0.1 vs localhost) for Windows browser compatibility.
 */

const BASE_URL_127 = 'http://127.0.0.1:8000';
const BASE_URL_LOCAL = 'http://localhost:8000';

let activeBaseUrl = import.meta.env.VITE_API_URL || BASE_URL_127;

/**
 * Universal safe fetch wrapper with dual-origin retry
 */
async function safeApiFetch(endpointPath, options = {}) {
  const primaryUrl = `${activeBaseUrl}${endpointPath}`;
  try {
    const response = await fetch(primaryUrl, options);
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || errData.error || `Server error: ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    // If primary failed due to network / connection refused, try fallback origin
    const altBase = activeBaseUrl.includes('127.0.0.1') ? BASE_URL_LOCAL : BASE_URL_127;
    const fallbackUrl = `${altBase}${endpointPath}`;
    try {
      const fallbackResponse = await fetch(fallbackUrl, options);
      if (!fallbackResponse.ok) {
        const errData = await fallbackResponse.json().catch(() => ({}));
        throw new Error(errData.detail || errData.error || `Server error: ${fallbackResponse.status}`);
      }
      activeBaseUrl = altBase; // Cache working origin
      return await fallbackResponse.json();
    } catch (fallbackErr) {
      if (err.message.includes('Failed to fetch') || fallbackErr.message.includes('Failed to fetch')) {
        throw new Error(
          'Backend server is offline! Please start the server by running "python run.py" in your terminal.'
        );
      }
      throw fallbackErr;
    }
  }
}

/**
 * Checks backend health
 */
export async function fetchHealth() {
  return await safeApiFetch('/health');
}

/**
 * Fetches list of distribution depots and regional buyer locations
 */
export async function getLocations() {
  return await safeApiFetch('/api/locations');
}

/**
 * Requests ML price & demand forecasting for selected crop and date
 */
export async function getForecast(crop, date) {
  return await safeApiFetch('/api/forecast', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ crop, date }),
  });
}

/**
 * Requests profit-maximizing crop allocation
 */
export async function allocateCrop(payload) {
  return await safeApiFetch('/api/allocate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}

/**
 * Solves CVRP and retrieves vehicle routes with exact OSRM road geometry
 */
export async function optimizeRoutes(crop, allocations, vehicleCapacities = null) {
  const payload = {
    crop,
    allocations,
  };
  if (vehicleCapacities) {
    payload.vehicle_capacities = vehicleCapacities;
  }

  return await safeApiFetch('/api/optimize-route', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}

/**
 * Master orchestration end-to-end optimization (Forecast -> Allocation -> CVRP -> Geometry)
 */
export async function masterOptimize(payload) {
  return await safeApiFetch('/api/optimize', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}
