// frontend/src/App.jsx
import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import DemandPanel from './components/DemandPanel';
import VehiclePanel from './components/VehiclePanel';
import MapView from './components/MapView';
import RoutePanel from './components/RoutePanel';
import { fetchHealth, getLocations, getForecast, allocateCrop, optimizeRoutes, masterOptimize } from './services/api';
import { AlertTriangle, CheckCircle2, RotateCcw, TrendingUp } from 'lucide-react';

const INITIAL_LOCATIONS = [
  { id: 0, name: 'Delhi',     latitude: 28.6139, longitude: 77.2090, is_depot: true },
  { id: 1, name: 'Noida',     latitude: 28.5355, longitude: 77.3910, is_depot: false },
  { id: 2, name: 'Ghaziabad', latitude: 28.6692, longitude: 77.4538, is_depot: false },
  { id: 3, name: 'Gurugram',  latitude: 28.4595, longitude: 77.0266, is_depot: false },
  { id: 4, name: 'Faridabad', latitude: 28.4089, longitude: 77.3178, is_depot: false },
  { id: 5, name: 'Sonipat',   latitude: 28.9931, longitude: 77.0151, is_depot: false },
  { id: 6, name: 'Panipat',   latitude: 29.3909, longitude: 76.9635, is_depot: false },
  { id: 7, name: 'Meerut',    latitude: 28.9845, longitude: 77.7064, is_depot: false },
  { id: 8, name: 'Rohtak',    latitude: 28.8955, longitude: 76.6066, is_depot: false },
];

/* ── Error Boundary ───────────────────────────────────────────── */
class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  componentDidCatch(error, info) { console.error('Portal error:', error, info); }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ minHeight: '100vh', background: 'var(--bg-base)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
          <div style={{ maxWidth: 400, background: 'var(--bg-raised)', border: '1.5px solid var(--beige-border)', borderRadius: 'var(--radius-md)', padding: '2rem', textAlign: 'center' }}>
            <AlertTriangle size={32} color="var(--red-muted)" style={{ margin: '0 auto 1rem' }} />
            <h2 className="font-display" style={{ fontSize: '1.2rem', color: 'var(--text-ink)', marginBottom: '0.5rem' }}>
              Dashboard Error
            </h2>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
              {this.state.error?.message || 'An unexpected error occurred.'}
            </p>
            <button className="btn-primary" onClick={() => { this.setState({ hasError: false }); window.location.reload(); }}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
              <RotateCcw size={13} /> Reload
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  return <ErrorBoundary><MainDashboard /></ErrorBoundary>;
}

/* ── Main Dashboard ───────────────────────────────────────────── */
function MainDashboard() {
  const [backendConnected, setBackendConnected] = useState(false);
  const [locations, setLocations]   = useState(INITIAL_LOCATIONS);
  const [crop, setCrop]             = useState('Wheat');
  const todayStr = new Date().toISOString().split('T')[0];
  const [date, setDate]             = useState(todayStr);
  const [availableSupply, setAvailableSupply] = useState(100000);
  const [priceMarkup, setPriceMarkup]         = useState(5.0);
  const [coverageMode]              = useState('maximum_profit');
  const [demands, setDemands]       = useState({
    Noida: 14287, Ghaziabad: 13613, Gurugram: 12492, Faridabad: 12207,
    Sonipat: 11513, Panipat: 11038, Meerut: 12860, Rohtak: 10675,
  });
  const [rawDemands, setRawDemands] = useState({
    Noida: 14287, Ghaziabad: 13613, Gurugram: 12492, Faridabad: 12207,
    Sonipat: 11513, Panipat: 11038, Meerut: 12860, Rohtak: 10675,
  });
  const [predictedPrices, setPredictedPrices] = useState({
    Delhi: 50.0, Noida: 52.0, Ghaziabad: 51.0, Gurugram: 55.0,
    Faridabad: 49.0, Sonipat: 48.0, Panipat: 47.0, Meerut: 52.0, Rohtak: 46.0,
  });
  const [vehicleCapacities]         = useState([20000, 22000, 25000, 28000, 30000]);
  const [masterResult, setMasterResult]       = useState(null);
  const [selectedVehicleId, setSelectedVehicleId] = useState(null);
  const [loadingForecast, setLoadingForecast] = useState(false);
  const [allocating, setAllocating]           = useState(false);
  const [optimizing, setOptimizing]           = useState(false);
  const [statusMessage, setStatusMessage]     = useState(null);

  useEffect(() => {
    (async () => {
      try {
        await fetchHealth();
        setBackendConnected(true);
        const locs = await getLocations();
        if (locs?.length) setLocations(locs);
      } catch { setBackendConnected(false); }
    })();
  }, []);

  const fetchForecastForCropAndDate = useCallback(async (selCrop, selDate, autoRecalc = false) => {
    setLoadingForecast(true);
    try {
      const data = await getForecast(selCrop, selDate);
      const newDemands = {}, newPrices = {};
      data.markets.forEach(m => {
        newPrices[m.location] = m.predicted_price_per_kg;
        if (m.location !== 'Delhi') newDemands[m.location] = m.expected_demand_kg;
      });
      setDemands(newDemands);
      setRawDemands(newDemands);
      setPredictedPrices(newPrices);
      const pv = Object.values(newPrices).filter(Boolean);
      const avgP = pv.length ? (pv.reduce((a, b) => a + b, 0) / pv.length).toFixed(2) : '—';

      if (autoRecalc) {
        const res = await masterOptimize({ crop: selCrop, date: selDate, available_quantity_kg: availableSupply, price_adjustment_percent: priceMarkup, coverage_mode: coverageMode, overrides: newDemands });
        setMasterResult(res);
        setStatusMessage({ type: 'success', text: `${selCrop} · ${selDate} — Avg ₹${avgP}/kg · Revenue ₹${(res.profit_summary?.expected_revenue || 0).toLocaleString()} · Profit ₹${(res.profit_summary?.expected_net_profit || 0).toLocaleString()}` });
      } else {
        setStatusMessage({ type: 'success', text: `ML forecast loaded for ${selCrop} (${selDate}) — Avg mandi price: ₹${avgP}/kg` });
      }
    } catch (err) {
      setStatusMessage({ type: 'error', text: `Forecast failed: ${err.message}` });
    } finally { setLoadingForecast(false); }
  }, [availableSupply, priceMarkup, coverageMode]);

  const handleCropChange = (v) => { setCrop(v); fetchForecastForCropAndDate(v, date, masterResult !== null); };
  const handleDateChange = (v) => {
    const today = new Date().toISOString().split('T')[0];
    const chosenDate = v < today ? today : v;
    setDate(chosenDate);
    fetchForecastForCropAndDate(crop, chosenDate, masterResult !== null);
  };

  const handlePriceMarkupChange = (v) => {
    setPriceMarkup(v);
    if (masterResult) {
      const allocKg = masterResult.supply?.allocated_kg || 0;
      const pv = Object.values(predictedPrices).filter(x => x > 0);
      const avg = pv.length ? pv.reduce((a, b) => a + b, 0) / pv.length : (crop === 'Onion' ? 50 : crop === 'Rice' ? 48 : crop === 'Maize' ? 24 : 34);
      const rev = Math.round(allocKg * avg * (1 + v / 100));
      const cost = masterResult.profit_summary?.estimated_logistics_cost || 0;
      const profit = Math.round(rev - cost);
      setMasterResult(prev => ({ ...prev, profit_summary: { ...prev.profit_summary, expected_revenue: rev, expected_net_profit: profit, expected_margin_percent: rev > 0 ? Number(((profit / rev) * 100).toFixed(2)) : 0 } }));
    }
  };

  const handleDemandChange = (loc, val) => setDemands(prev => ({ ...prev, [loc]: val }));
  const handleFetchForecast = () => fetchForecastForCropAndDate(crop, date, false);

  const handleAllocate = async () => {
    setAllocating(true); setStatusMessage(null);
    try {
      const res = await allocateCrop({ crop, date, available_quantity_kg: availableSupply, price_adjustment_percent: priceMarkup, coverage_mode: coverageMode });
      const nd = {};
      res.markets.forEach(m => { if (m.location !== 'Delhi') nd[m.location] = m.allocated_kg; });
      setDemands(nd);
      setMasterResult(prev => ({ ...prev, supply: res.supply, profit_summary: res.profit_summary, routing_summary: prev?.routing_summary || { vehicles_used: 0, vehicles_available: 5, total_distance_km: 0, total_duration_minutes: 0, fleet_utilization_percent: 0 }, routes: prev?.routes || [] }));
      setStatusMessage({ type: 'success', text: `Profit allocation solved for ${crop} — ${(res.supply.allocated_kg / 1000).toFixed(1)}t allocated · Net Profit ₹${res.profit_summary.expected_net_profit.toLocaleString()}` });
    } catch (err) { setStatusMessage({ type: 'error', text: `Allocation failed: ${err.message}` }); }
    finally { setAllocating(false); }
  };

  const handleOptimizeRoutes = async () => {
    setOptimizing(true); setStatusMessage(null); setSelectedVehicleId(null);
    try {
      // Scale market demands proportionally to availableSupply if supply < total market demand
      let effectiveDemands = { ...demands };
      const totalDemandKg = Object.values(demands).reduce((a, v) => a + (Number(v) || 0), 0);
      if (totalDemandKg > 0 && availableSupply < totalDemandKg) {
        const scale = availableSupply / totalDemandKg;
        Object.keys(effectiveDemands).forEach(loc => {
          effectiveDemands[loc] = Math.round(effectiveDemands[loc] * scale);
        });
        setDemands(effectiveDemands);
      }

      const res = await optimizeRoutes(crop, effectiveDemands, vehicleCapacities);
      const delivered = (res.routes || []).reduce((a, r) => a + (r.load_kg || 0), 0);
      const pv = Object.values(predictedPrices).filter(x => x > 0);
      const avg = pv.length ? pv.reduce((a, b) => a + b, 0) / pv.length : (crop === 'Onion' ? 50 : crop === 'Rice' ? 48 : crop === 'Maize' ? 24 : 34);
      const rev = Math.round(delivered * avg * (1 + priceMarkup / 100));
      const cost = Math.round((res.routing_summary?.total_distance_km || 0) * 100);
      setMasterResult(prev => ({
        supply: prev?.supply || { available_quantity_kg: availableSupply, allocated_kg: delivered, surplus_kg: Math.max(0, availableSupply - delivered) },
        profit_summary: prev?.profit_summary || { expected_revenue: rev, estimated_logistics_cost: cost, expected_net_profit: rev - cost, expected_margin_percent: rev > 0 ? Number(((rev - cost) / rev * 100).toFixed(2)) : 0 },
        routing_summary: res.routing_summary, routes: res.routes || [],
      }));
      setStatusMessage({ type: 'success', text: `Routing solved for ${(delivered / 1000).toFixed(1)}t supply — ${res.routing_summary?.vehicles_used || res.routes?.length || 0} trucks · ${res.routing_summary?.total_distance_km || 0} km · Transport cost ₹${cost.toLocaleString()}` });
    } catch (err) { setStatusMessage({ type: 'error', text: `Route optimization failed: ${err.message}` }); }
    finally { setOptimizing(false); }
  };

  const handleMasterOptimize = async () => {
    setOptimizing(true); setStatusMessage(null); setSelectedVehicleId(null);
    try {
      const res = await masterOptimize({ crop, date, available_quantity_kg: availableSupply, price_adjustment_percent: priceMarkup, coverage_mode: coverageMode, overrides: demands });
      setMasterResult(res);

      // Update market demands in UI to reflect exact allocated supply
      const allocatedMap = {};
      (res.markets || []).forEach(m => {
        if (m.location !== 'Delhi') allocatedMap[m.location] = m.allocated_kg;
      });
      if (Object.keys(allocatedMap).length > 0) {
        setDemands(allocatedMap);
      }

      setStatusMessage({ type: 'success', text: `Full optimization complete for ${crop} — ${((res.supply?.allocated_kg || 0) / 1000).toFixed(1)}t across ${res.routing_summary?.vehicles_used || 0} trucks · Net Profit ₹${(res.profit_summary?.expected_net_profit || 0).toLocaleString()}` });
    } catch (err) { setStatusMessage({ type: 'error', text: `Optimization failed: ${err.message}` }); }
    finally { setOptimizing(false); }
  };

  const handleWarehouseStore = (leftoverKg) => {
    const tons = (leftoverKg / 1000).toFixed(1);
    setStatusMessage({
      type: 'success',
      text: `📦 Warehouse Storage Initiated: ${tons} tons of surplus ${crop} registered for Phase 2 warehouse storage integration.`
    });
  };

  const totalDemand = Object.values(demands).reduce((a, v) => a + (Number(v) || 0), 0);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)', display: 'flex', flexDirection: 'column' }}>
      <Header backendConnected={backendConnected} />

      <main style={{ flex: 1, maxWidth: 1400, width: '100%', margin: '0 auto', padding: '1.5rem 2rem 3rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

        {/* ── Status Banner ── */}
        {statusMessage && (
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '0.7rem 1rem',
            background: statusMessage.type === 'error' ? 'var(--red-pale)' : 'var(--green-pale)',
            border: `1.5px solid ${statusMessage.type === 'error' ? '#D4A0A0' : 'var(--green-light)'}`,
            borderRadius: 'var(--radius-sm)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              {statusMessage.type === 'error'
                ? <AlertTriangle size={14} color="var(--red-muted)" style={{ flexShrink: 0 }} />
                : <CheckCircle2 size={14} color="var(--green-deep)" style={{ flexShrink: 0 }} />}
              <span style={{ fontSize: '0.78rem', fontWeight: 600, color: statusMessage.type === 'error' ? 'var(--red-muted)' : 'var(--green-deep)' }}>
                {statusMessage.text}
              </span>
            </div>
            <button onClick={() => setStatusMessage(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '0.68rem', color: 'var(--text-faint)', fontWeight: 700 }}>
              ✕
            </button>
          </div>
        )}

        {/* ── KPI Bar ── */}
        {masterResult && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '0.6rem' }}>
            {[
              { label: 'Allocated Supply', val: `${((masterResult.supply?.allocated_kg || 0) / 1000).toFixed(1)}`, unit: 'Tons', sub: `Surplus: ${((masterResult.supply?.surplus_kg || 0) / 1000).toFixed(1)}t`, accent: false },
              { label: 'Expected Revenue', val: `₹${(masterResult.profit_summary?.expected_revenue || 0).toLocaleString()}`, unit: '', sub: `SP +${priceMarkup}% (${crop})`, accent: 'green' },
              { label: 'Transport Cost', val: `₹${(masterResult.profit_summary?.estimated_logistics_cost || 0).toLocaleString()}`, unit: '', sub: `${masterResult.routing_summary?.total_distance_km || 0} km @ ₹100/km`, accent: 'red' },
              { label: 'Net Profit', val: `₹${(masterResult.profit_summary?.expected_net_profit || 0).toLocaleString()}`, unit: '', sub: `Margin: ${masterResult.profit_summary?.expected_margin_percent || 0}%`, accent: 'green' },
              { label: 'Vehicles Used', val: `${masterResult.routing_summary?.vehicles_used || masterResult.routes?.length || 0}/${masterResult.routing_summary?.vehicles_available || 5}`, unit: '', sub: `Utilization: ${masterResult.routing_summary?.fleet_utilization_percent || 0}%`, accent: false },
              { label: 'Travel Time', val: `${(((masterResult.routing_summary?.total_duration_minutes || 0)) / 60).toFixed(1)}`, unit: 'hrs', sub: `${masterResult.routing_summary?.total_duration_minutes || 0} mins`, accent: false },
            ].map(({ label, val, unit, sub, accent }) => (
              <div key={label} className="kpi-block" style={{
                '--kpi-accent': accent === 'green' ? 'var(--green-mid)' : accent === 'red' ? 'var(--red-muted)' : 'var(--beige-mid)',
              }}>
                <p className="text-label-caps" style={{ color: 'var(--text-faint)', margin: '0 0 0.3rem' }}>{label}</p>
                <p className="font-mono-data" style={{
                  fontSize: '1.05rem', fontWeight: 500, margin: 0,
                  color: accent === 'green' ? 'var(--green-deep)' : accent === 'red' ? 'var(--red-muted)' : 'var(--text-ink)',
                }}>
                  {val} <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{unit}</span>
                </p>
                <p style={{ fontSize: '0.62rem', color: 'var(--text-faint)', margin: '0.2rem 0 0' }}>{sub}</p>
              </div>
            ))}
          </div>
        )}

        {/* ── Asymmetric Two-Column Grid ── */}
        <div className="grid-asymmetric">

          {/* LEFT — Farmer Controls (narrower col) */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <DemandPanel
              crop={crop} setCrop={handleCropChange}
              date={date} setDate={handleDateChange}
              availableSupply={availableSupply} setAvailableSupply={setAvailableSupply}
              priceMarkup={priceMarkup} setPriceMarkup={handlePriceMarkupChange}
              coverageMode={coverageMode} setCoverageMode={() => {}}
              demands={demands} rawDemands={rawDemands} predictedPrices={predictedPrices}
              vehicleCapacities={vehicleCapacities}
              onDemandChange={handleDemandChange}
              onFetchForecast={handleFetchForecast}
              onAllocate={handleAllocate}
              onOptimizeRoutes={handleOptimizeRoutes}
              onMasterOptimize={handleMasterOptimize}
              onWarehouseStore={handleWarehouseStore}
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

          {/* RIGHT — Map + Routes (wider col) */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>

            {/* Map Panel — offset slightly for asymmetry */}
            <div className="panel-raised" style={{ padding: '0.85rem', borderRadius: 'var(--radius-md)', marginTop: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
                <h3 className="font-display" style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-ink)', margin: 0 }}>
                  Delhi-NCR Route Map
                </h3>
                <span className="text-label-caps" style={{ color: 'var(--text-faint)' }}>
                  {masterResult?.routes?.length ? `${masterResult.routes.length} active truck routes` : 'Central depot: Delhi'}
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
              optimizationResult={masterResult ? { routes: masterResult.routes || [], summary: masterResult.routing_summary || {} } : null}
              selectedVehicleId={selectedVehicleId}
              onSelectVehicle={setSelectedVehicleId}
            />
          </div>

        </div>
      </main>

      {/* Footer */}
      <footer style={{ background: 'var(--bg-raised)', borderTop: '1px solid var(--beige-border)', padding: '0.9rem 2rem' }}>
        <p className="text-label-caps" style={{ color: 'var(--text-faint)', textAlign: 'center', margin: 0 }}>
          AgriRoute AI · OR-Tools CVRP · OSRM Road Geometry · FastAPI · React · Leaflet
        </p>
      </footer>
    </div>
  );
}
