// frontend/src/App.jsx
import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import DemandPanel from './components/DemandPanel';
import VehiclePanel from './components/VehiclePanel';
import MapView from './components/MapView';
import RoutePanel from './components/RoutePanel';
import { fetchHealth, getLocations, getForecast, allocateCrop, optimizeRoutes, masterOptimize } from './services/api';
import { AlertTriangle, CheckCircle2, RotateCcw } from 'lucide-react';

const INITIAL_LOCATIONS = [
  { id: 0, name: 'Delhi', latitude: 28.6139, longitude: 77.2090, is_depot: true },
  { id: 1, name: 'Noida', latitude: 28.5355, longitude: 77.3910, is_depot: false },
  { id: 2, name: 'Ghaziabad', latitude: 28.6692, longitude: 77.4538, is_depot: false },
  { id: 3, name: 'Gurugram', latitude: 28.4595, longitude: 77.0266, is_depot: false },
  { id: 4, name: 'Faridabad', latitude: 28.4089, longitude: 77.3178, is_depot: false },
  { id: 5, name: 'Sonipat', latitude: 28.9931, longitude: 77.0151, is_depot: false },
  { id: 6, name: 'Panipat', latitude: 29.3909, longitude: 76.9635, is_depot: false },
  { id: 7, name: 'Meerut', latitude: 28.9845, longitude: 77.7064, is_depot: false },
  { id: 8, name: 'Rohtak', latitude: 28.8955, longitude: 76.6066, is_depot: false },
];

// Error boundary to prevent white screen crashes
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Portal caught UI error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-white rounded-2xl shadow-lg border border-rose-100 p-6 text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-bold text-slate-900">Dashboard Encountered an Issue</h2>
            <p className="text-xs text-slate-500">
              {this.state.error?.message || 'An unexpected rendering error occurred.'}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
              className="inline-flex items-center space-x-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-4 py-2 rounded-xl text-xs transition shadow-sm"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Reload Application</span>
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  return (
    <ErrorBoundary>
      <MainDashboard />
    </ErrorBoundary>
  );
}

function MainDashboard() {
  const [backendConnected, setBackendConnected] = useState(false);
  const [locations, setLocations] = useState(INITIAL_LOCATIONS);
  const [crop, setCrop] = useState('Wheat');
  const [date, setDate] = useState('2026-09-02');
  const [availableSupply, setAvailableSupply] = useState(100000); // 100 Tons
  const [priceMarkup, setPriceMarkup] = useState(5.0); // +5% Price Markup
  const [coverageMode, setCoverageMode] = useState('maximum_profit');

  const [demands, setDemands] = useState({
    Noida: 14287,
    Ghaziabad: 13613,
    Gurugram: 12492,
    Faridabad: 12207,
    Sonipat: 11513,
    Panipat: 11038,
    Meerut: 12860,
    Rohtak: 10675,
  });

  // Predicted prices per market returned from ML forecast model
  const [predictedPrices, setPredictedPrices] = useState({
    Delhi: 50.0, Noida: 52.0, Ghaziabad: 51.0, Gurugram: 55.0,
    Faridabad: 49.0, Sonipat: 48.0, Panipat: 47.0, Meerut: 52.0, Rohtak: 46.0,
  });

  const [vehicleCapacities] = useState([20000, 22000, 25000, 28000, 30000]);
  const [masterResult, setMasterResult] = useState(null);
  const [selectedVehicleId, setSelectedVehicleId] = useState(null);

  const [loadingForecast, setLoadingForecast] = useState(false);
  const [allocating, setAllocating] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);

  // Initialize backend connection
  useEffect(() => {
    async function init() {
      try {
        await fetchHealth();
        setBackendConnected(true);
        const locs = await getLocations();
        if (locs && locs.length > 0) {
          setLocations(locs);
        }
      } catch (err) {
        console.error('Initialization error:', err);
        setBackendConnected(false);
      }
    }
    init();
  }, []);

  // Fetch forecast function
  const fetchForecastForCropAndDate = useCallback(async (selectedCrop, selectedDate, autoRecalculate = false) => {
    setLoadingForecast(true);
    try {
      const forecastData = await getForecast(selectedCrop, selectedDate);
      const newDemands = {};
      const newPrices = {};

      forecastData.markets.forEach((m) => {
        newPrices[m.location] = m.predicted_price_per_kg;
        if (m.location !== 'Delhi') {
          newDemands[m.location] = m.expected_demand_kg;
        }
      });

      setDemands(newDemands);
      setPredictedPrices(newPrices);

      // Compute weighted avg price across markets for status display
      const priceVals = Object.values(newPrices).filter(Boolean);
      const avgPrice = priceVals.length > 0
        ? (priceVals.reduce((a, b) => a + b, 0) / priceVals.length).toFixed(2)
        : '—';

      if (autoRecalculate) {
        const payload = {
          crop: selectedCrop,
          date: selectedDate,
          available_quantity_kg: availableSupply,
          price_adjustment_percent: priceMarkup,
          coverage_mode: coverageMode,
          overrides: newDemands,
        };
        const res = await masterOptimize(payload);
        setMasterResult(res);
        setStatusMessage({
          type: 'success',
          text: `${selectedCrop} (${selectedDate}): Avg market price ₹${avgPrice}/kg → Revenue ₹${(res.profit_summary?.expected_revenue || 0).toLocaleString()}, Net Profit ₹${(res.profit_summary?.expected_net_profit || 0).toLocaleString()}`,
        });
      } else {
        setStatusMessage({
          type: 'success',
          text: `ML forecast loaded for ${selectedCrop} on ${selectedDate} — Avg mandi price: ₹${avgPrice}/kg`,
        });
      }
    } catch (err) {
      console.error('Forecast error:', err);
      setStatusMessage({
        type: 'error',
        text: `Forecast fetch failed: ${err.message}`,
      });
    } finally {
      setLoadingForecast(false);
    }
  }, [availableSupply, priceMarkup, coverageMode]);

  // AUTO-TRIGGER: Whenever user changes crop or date, automatically fetch new demands and recalculate values!
  const handleCropChange = (newCrop) => {
    setCrop(newCrop);
    fetchForecastForCropAndDate(newCrop, date, masterResult !== null);
  };

  const handleDateChange = (newDate) => {
    setDate(newDate);
    fetchForecastForCropAndDate(crop, newDate, masterResult !== null);
  };

  // REAL-TIME SELLING PRICE (SP) MARKUP SLIDER HANDLER:
  // Uses the ML-predicted prices (not static base) so revenue reacts to both date AND markup changes
  const handlePriceMarkupChange = (newMarkup) => {
    setPriceMarkup(newMarkup);
    if (masterResult) {
      const allocatedKg = masterResult.supply?.allocated_kg || 0;
      // Use ML-predicted avg price as base — changes with every date!
      const priceVals = Object.values(predictedPrices).filter(v => v > 0);
      const avgPredictedPrice = priceVals.length > 0
        ? priceVals.reduce((a, b) => a + b, 0) / priceVals.length
        : (crop === 'Onion' ? 50.0 : crop === 'Rice' ? 48.0 : 34.0);
      const markedUpPrice = avgPredictedPrice * (1.0 + (newMarkup / 100.0));
      const newRevenue = Math.round(allocatedKg * markedUpPrice);
      const transportCost = masterResult.profit_summary?.estimated_logistics_cost || 0;
      const newProfit = Math.round(newRevenue - transportCost);
      const newMargin = newRevenue > 0 ? Number(((newProfit / newRevenue) * 100).toFixed(2)) : 0;

      setMasterResult((prev) => ({
        ...prev,
        profit_summary: {
          ...prev.profit_summary,
          expected_revenue: newRevenue,
          expected_net_profit: newProfit,
          expected_margin_percent: newMargin,
        }
      }));
    }
  };

  const handleDemandChange = (locName, val) => {
    setDemands((prev) => ({
      ...prev,
      [locName]: val,
    }));
  };

  // 1. Manual button: Fetch AI Forecast
  const handleFetchForecast = () => {
    fetchForecastForCropAndDate(crop, date, false);
  };

  // 2. Action: Optimize Profit Allocation (/api/allocate)
  const handleAllocate = async () => {
    setAllocating(true);
    setStatusMessage(null);
    try {
      const payload = {
        crop,
        date,
        available_quantity_kg: availableSupply,
        price_adjustment_percent: priceMarkup,
        coverage_mode: coverageMode,
      };
      const res = await allocateCrop(payload);

      // Update farmer inputs with allocated quantities
      const newDemands = {};
      res.markets.forEach((m) => {
        if (m.location !== 'Delhi') {
          newDemands[m.location] = m.allocated_kg;
        }
      });
      setDemands(newDemands);

      setMasterResult((prev) => ({
        ...prev,
        supply: res.supply,
        profit_summary: res.profit_summary,
        routing_summary: prev?.routing_summary || {
          vehicles_used: 0,
          vehicles_available: 5,
          total_distance_km: 0,
          total_duration_minutes: 0,
          fleet_utilization_percent: 0,
        },
        routes: prev?.routes || [],
      }));

      setStatusMessage({
        type: 'success',
        text: `Profit allocation solved for ${crop}! Allocated ${(res.supply.allocated_kg / 1000).toFixed(1)} tons. Expected Net Profit: ₹${res.profit_summary.expected_net_profit.toLocaleString()}`,
      });
    } catch (err) {
      console.error('Allocation error:', err);
      setStatusMessage({
        type: 'error',
        text: `Profit optimization failed: ${err.message}`,
      });
    } finally {
      setAllocating(false);
    }
  };

  // 3. Action: Optimize Vehicle Routes (/api/optimize-route)
  const handleOptimizeRoutes = async () => {
    setOptimizing(true);
    setStatusMessage(null);
    setSelectedVehicleId(null);
    try {
      const res = await optimizeRoutes(crop, demands, vehicleCapacities);
      const totalDelivered = (res.routes || []).reduce((acc, r) => acc + (r.load_kg || 0), 0);

      const priceValsR = Object.values(predictedPrices).filter(v => v > 0);
      const avgPredictedPriceR = priceValsR.length > 0
        ? priceValsR.reduce((a, b) => a + b, 0) / priceValsR.length
        : (crop === 'Onion' ? 50.0 : crop === 'Rice' ? 48.0 : 34.0);
      const markedUpPrice = avgPredictedPriceR * (1.0 + (priceMarkup / 100.0));
      const rev = Math.round(totalDelivered * markedUpPrice);
      const cost = Math.round((res.routing_summary?.total_distance_km || 0) * 100.0); // ₹100/km commercial freight

      setMasterResult((prev) => ({
        supply: prev?.supply || {
          available_quantity_kg: availableSupply,
          allocated_kg: totalDelivered,
          surplus_kg: Math.max(0, availableSupply - totalDelivered),
        },
        profit_summary: prev?.profit_summary || {
          expected_revenue: rev,
          estimated_logistics_cost: cost,
          expected_net_profit: rev - cost,
          expected_margin_percent: rev > 0 ? Number(((rev - cost) / rev * 100).toFixed(2)) : 0,
        },
        routing_summary: res.routing_summary,
        routes: res.routes || [],
      }));

      setStatusMessage({
        type: 'success',
        text: `Vehicle routing solved! ${res.routing_summary?.vehicles_used || res.routes?.length || 0} trucks dispatched. Total road distance: ${res.routing_summary?.total_distance_km || 0} km (Transport cost: ₹${cost.toLocaleString()}).`,
      });
    } catch (err) {
      console.error('Route optimization error:', err);
      setStatusMessage({
        type: 'error',
        text: `Route optimization failed: ${err.message}`,
      });
    } finally {
      setOptimizing(false);
    }
  };

  // 4. Action: Master End-to-End Orchestration (/api/optimize)
  const handleMasterOptimize = async () => {
    setOptimizing(true);
    setStatusMessage(null);
    setSelectedVehicleId(null);
    try {
      const payload = {
        crop,
        date,
        available_quantity_kg: availableSupply,
        price_adjustment_percent: priceMarkup,
        coverage_mode: coverageMode,
        overrides: demands,
      };
      const res = await masterOptimize(payload);
      setMasterResult(res);
      setStatusMessage({
        type: 'success',
        text: `Full end-to-end optimization complete for ${crop}! Allocated ${((res.supply?.allocated_kg || 0) / 1000).toFixed(1)} tons across ${res.routing_summary?.vehicles_used || 0} delivery trucks. Net Profit: ₹${(res.profit_summary?.expected_net_profit || 0).toLocaleString()}`,
      });
    } catch (err) {
      console.error('Master optimization error:', err);
      setStatusMessage({
        type: 'error',
        text: `Master optimization failed: ${err.message}`,
      });
    } finally {
      setOptimizing(false);
    }
  };

  const totalDemand = Object.values(demands).reduce(
    (acc, curr) => acc + (Number(curr) || 0),
    0
  );

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Header backendConnected={backendConnected} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* Status Notification Banner */}
        {statusMessage && (
          <div
            className={`p-4 rounded-xl border flex items-center justify-between text-sm shadow-xs ${
              statusMessage.type === 'error'
                ? 'bg-rose-50 border-rose-200 text-rose-800'
                : 'bg-emerald-50 border-emerald-200 text-emerald-800'
            }`}
          >
            <div className="flex items-center space-x-2.5">
              {statusMessage.type === 'error' ? (
                <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
              ) : (
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              )}
              <span className="font-semibold">{statusMessage.text}</span>
            </div>
            <button
              onClick={() => setStatusMessage(null)}
              className="text-xs font-bold hover:underline opacity-80"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Financial & Logistics KPI Summary Cards */}
        {masterResult && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs space-y-1">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Allocated Supply</span>
              <p className="text-base font-extrabold text-slate-900">
                {(((masterResult.supply?.allocated_kg || 0)) / 1000).toFixed(1)} <span className="text-xs text-slate-500 font-medium">Tons</span>
              </p>
              <span className="text-[10px] text-slate-400 block">
                Surplus: {(((masterResult.supply?.surplus_kg || 0)) / 1000).toFixed(1)}t
              </span>
            </div>

            <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs space-y-1">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Expected Revenue</span>
              <p className="text-base font-extrabold text-emerald-600">
                ₹{(masterResult.profit_summary?.expected_revenue || 0).toLocaleString()}
              </p>
              <span className="text-[10px] text-slate-400 block">SP Markup: +{priceMarkup}% ({crop})</span>
            </div>

            <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs space-y-1">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Transport Cost</span>
              <p className="text-base font-extrabold text-rose-600">
                ₹{(masterResult.profit_summary?.estimated_logistics_cost || 0).toLocaleString()}
              </p>
              <span className="text-[10px] text-slate-400 block">{masterResult.routing_summary?.total_distance_km || 0} km @ ₹100/km</span>
            </div>

            <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs space-y-1">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Expected Net Profit</span>
              <p className="text-base font-extrabold text-emerald-700">
                ₹{(masterResult.profit_summary?.expected_net_profit || 0).toLocaleString()}
              </p>
              <span className="text-[10px] text-emerald-600 font-bold block">
                Margin: {masterResult.profit_summary?.expected_margin_percent || 0}%
              </span>
            </div>

            <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs space-y-1">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Vehicles Used</span>
              <p className="text-base font-extrabold text-blue-600">
                {masterResult.routing_summary?.vehicles_used || masterResult.routes?.length || 0} / {masterResult.routing_summary?.vehicles_available || 5}
              </p>
              <span className="text-[10px] text-slate-400 block">
                Utilization: {masterResult.routing_summary?.fleet_utilization_percent || 0}%
              </span>
            </div>

            <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs space-y-1">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Total Travel Time</span>
              <p className="text-base font-extrabold text-slate-800">
                {(((masterResult.routing_summary?.total_duration_minutes || 0)) / 60).toFixed(1)} <span className="text-xs text-slate-500 font-medium">Hours</span>
              </p>
              <span className="text-[10px] text-slate-400 block">
                {masterResult.routing_summary?.total_duration_minutes || 0} mins
              </span>
            </div>
          </div>
        )}

        {/* Dashboard 2-Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Left Column: Farmer Controls (5 cols) */}
          <div className="lg:col-span-5 space-y-6">
            <DemandPanel
              crop={crop}
              setCrop={handleCropChange}
              date={date}
              setDate={handleDateChange}
              availableSupply={availableSupply}
              setAvailableSupply={setAvailableSupply}
              priceMarkup={priceMarkup}
              setPriceMarkup={handlePriceMarkupChange}
              coverageMode={coverageMode}
              setCoverageMode={setCoverageMode}
              demands={demands}
              predictedPrices={predictedPrices}
              onDemandChange={handleDemandChange}
              onFetchForecast={handleFetchForecast}
              onAllocate={handleAllocate}
              onOptimizeRoutes={handleOptimizeRoutes}
              onMasterOptimize={handleMasterOptimize}
              loadingForecast={loadingForecast}
              allocating={allocating}
              optimizing={optimizing}
              locations={locations}
            />

            <VehiclePanel
              vehicleCapacities={vehicleCapacities}
              totalDemand={totalDemand}
              routes={masterResult?.routes || []}
            />
          </div>

          {/* Right Column: Map & Vehicle Routes (7 cols) */}
          <div className="lg:col-span-7 space-y-6">
            <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm space-y-2">
              <div className="flex items-center justify-between px-2 pt-1">
                <h3 className="font-bold text-slate-800 text-sm">
                  Delhi-NCR Route Map & Road Geometry
                </h3>
                <span className="text-xs text-slate-500 font-semibold">
                  {masterResult?.routes?.length ? `${masterResult.routes.length} Active Truck Routes` : 'Central Depot: Delhi'}
                </span>
              </div>
              <MapView
                locations={locations}
                demands={demands}
                routes={masterResult?.routes || []}
                selectedVehicleId={selectedVehicleId}
                onSelectVehicle={setSelectedVehicleId}
              />
            </div>

            <RoutePanel
              optimizationResult={masterResult ? {
                routes: masterResult.routes || [],
                summary: masterResult.routing_summary || {}
              } : null}
              selectedVehicleId={selectedVehicleId}
              onSelectVehicle={setSelectedVehicleId}
            />
          </div>

        </div>

      </main>

      <footer className="bg-white border-t border-slate-200 py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs font-semibold text-slate-500">
          AI Agricultural Profit Optimization & Logistics Portal • Google OR-Tools CVRP + OSRM Routing + FastAPI + React + Leaflet
        </div>
      </footer>
    </div>
  );
}
