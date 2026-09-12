// frontend/src/components/DemandPanel.jsx
import React, { useState } from 'react';
import { Sparkles, MapPin, RefreshCw, ChevronRight, Plus, Minus, TrendingUp, Calculator, Truck, ArrowUpRight, Warehouse } from 'lucide-react';

const CROPS = ['Wheat', 'Rice', 'Onion', 'Maize'];

const CROP_META = {
  Wheat:  { emoji: '🌾', color: '#7A6030', paleBg: '#FBF5E0', borderColor: '#D4BC72' },
  Onion:  { emoji: '🧅', color: '#8B3A3A', paleBg: '#FAE8E8', borderColor: '#D4A0A0' },
  Rice:   { emoji: '🍚', color: '#3A6347', paleBg: '#E8F4EC', borderColor: '#9DC9A8' },
  Maize:  { emoji: '🌽', color: '#9A6B1F', paleBg: '#FEF9E7', borderColor: '#E6C687' },
};

const CROP_BENCHMARKS = {
  Wheat: { basePricePerKg: 34.0 },
  Onion: { basePricePerKg: 50.0 },
  Rice:  { basePricePerKg: 48.0 },
  Maize: { basePricePerKg: 24.0 },
};

// Section label component
const Label = ({ children }) => (
  <p className="text-label-caps" style={{ color: 'var(--text-faint)', marginBottom: '0.35rem' }}>{children}</p>
);

export default function DemandPanel({
  crop, setCrop, date, setDate,
  availableSupply, setAvailableSupply,
  priceMarkup, setPriceMarkup,
  coverageMode, setCoverageMode,
  demands, rawDemands = {}, predictedPrices = {},
  vehicleCapacities = [20000, 22000, 25000, 28000, 30000],
  onDemandChange, onFetchForecast,
  onAllocate, onOptimizeRoutes, onMasterOptimize, onWarehouseStore,
  loadingForecast, allocating, optimizing, locations,
}) {
  const [unitMode, setUnitMode] = useState('tons');

  const meta = CROP_META[crop] || CROP_META.Wheat;
  const benchmark = CROP_BENCHMARKS[crop] || CROP_BENCHMARKS.Wheat;
  const totalDemandKg = Object.values(demands).reduce((acc, v) => acc + (Number(v) || 0), 0);
  const totalRawDemandKg = Object.values(rawDemands).reduce((acc, v) => acc + (Number(v) || 0), 0);

  const maxTransportCapacityKg = vehicleCapacities.reduce((a, b) => a + b, 0);
  const maxTransportCapacityTons = (maxTransportCapacityKg / 1000).toFixed(0);
  const isExceedingCapacity = availableSupply > maxTransportCapacityKg;

  const leftoverKg = Math.max(0, availableSupply - totalRawDemandKg);
  const isSupplyLess = availableSupply < totalRawDemandKg;

  const priceVals = Object.values(predictedPrices).filter(v => v > 0);
  const mlAvgPrice = priceVals.length > 0
    ? priceVals.reduce((a, b) => a + b, 0) / priceVals.length
    : benchmark.basePricePerKg;

  const effectivePricePerKg = (mlAvgPrice * (1.0 + priceMarkup / 100.0)).toFixed(2);
  const effectiveCostPerTon = Math.round(mlAvgPrice * 1000 * (1.0 + priceMarkup / 100.0));
  const markupGainPerTon = Math.round(effectiveCostPerTon - mlAvgPrice * 1000);

  const getDisplayVal = (kgVal) =>
    unitMode === 'tons' ? (Number(kgVal || 0) / 1000).toString() : (Number(kgVal || 0)).toString();

  const handleInput = (locName, rawVal) => {
    const num = parseFloat(rawVal) || 0;
    const kgVal = unitMode === 'tons' ? Math.round(num * 1000) : Math.round(num);
    onDemandChange(locName, Math.max(0, kgVal));
  };

  const step = (locName, dir) => {
    const stepVal = unitMode === 'tons' ? 1000 : 500;
    onDemandChange(locName, Math.max(0, (demands[locName] || 0) + dir * stepVal));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>

      {/* ── PANEL 1: Controls ── */}
      <div className="panel" style={{ padding: '1.1rem' }}>

        {/* Panel Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--beige-border)' }}>
          <h2 className="font-display" style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-ink)', margin: 0 }}>
            Farmer Inputs
          </h2>
          {/* Unit Toggle */}
          <div style={{ display: 'flex', border: '1.5px solid var(--beige-border)', borderRadius: 'var(--radius-xs)', overflow: 'hidden' }}>
            {['tons', 'kg'].map(u => (
              <button key={u} onClick={() => setUnitMode(u)} style={{
                padding: '0.25rem 0.65rem',
                fontSize: '0.68rem', fontWeight: 700, fontFamily: 'DM Sans, sans-serif',
                background: unitMode === u ? 'var(--green-deep)' : 'transparent',
                color: unitMode === u ? '#FBF8F2' : 'var(--text-muted)',
                border: 'none', cursor: 'pointer',
              }}>{u}</button>
            ))}
          </div>
        </div>

        {/* Crop + Date row */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.85rem' }}>
          <div>
            <Label>Selected Crop</Label>
            <select className="field-select" value={crop} onChange={e => setCrop(e.target.value)}>
              {CROPS.map(c => <option key={c} value={c}>{CROP_META[c].emoji} {c}</option>)}
            </select>
          </div>
          <div>
            <Label>Prediction Date</Label>
            <input
              type="date"
              className="field-input"
              value={date}
              min={new Date().toISOString().split('T')[0]}
              onChange={e => setDate(e.target.value)}
            />
          </div>
        </div>

        {/* Crop Pricing Card */}
        <div style={{
          background: meta.paleBg,
          border: `1.5px solid ${meta.borderColor}`,
          borderRadius: 'var(--radius-sm)',
          padding: '0.75rem',
          marginBottom: '0.85rem',
          display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem',
        }}>
          <div>
            <p className="text-label-caps" style={{ color: meta.color, margin: '0 0 0.2rem' }}>Cost of 1 Ton</p>
            <p className="font-mono-data" style={{ fontSize: '1.1rem', fontWeight: 500, color: 'var(--text-ink)', margin: 0 }}>
              ₹{effectiveCostPerTon.toLocaleString()}
              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginLeft: '0.3rem' }}>/ ton</span>
            </p>
            <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', margin: '0.2rem 0 0' }}>
              ₹{effectivePricePerKg}/kg (ML predicted)
              {priceMarkup > 0 && (
                <span style={{ color: 'var(--green-deep)', marginLeft: '0.3rem', fontWeight: 700 }}>
                  +₹{markupGainPerTon.toLocaleString()}/t markup
                </span>
              )}
            </p>
          </div>
          <div>
            <p className="text-label-caps" style={{ color: meta.color, margin: '0 0 0.2rem' }}>Transport Rate</p>
            <p className="font-mono-data" style={{ fontSize: '1.1rem', fontWeight: 500, color: 'var(--text-ink)', margin: 0 }}>
              ₹100<span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginLeft: '0.2rem' }}>/ km</span>
            </p>
            <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', margin: '0.2rem 0 0' }}>
              ₹10.00 per Ton / km freight
            </p>
          </div>
        </div>

        {/* Supply Input */}
        <div style={{ marginBottom: '0.85rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.3rem' }}>
            <Label>Total Available Supply</Label>
            <div style={{ textAlign: 'right' }}>
              <span className="font-mono-data" style={{ fontSize: '0.72rem', color: isExceedingCapacity ? 'var(--amber-warm)' : 'var(--green-deep)', fontWeight: 600 }}>
                {(availableSupply / 1000).toFixed(1)} tons
              </span>
              <span style={{ fontSize: '0.62rem', color: 'var(--text-faint)', display: 'block' }}>
                Upper Limit: {maxTransportCapacityTons}t fleet cap
              </span>
            </div>
          </div>
          <input
            type="number" min="1000" step="1000" className="field-input"
            value={unitMode === 'tons' ? availableSupply / 1000 : availableSupply}
            onChange={e => {
              const raw = parseFloat(e.target.value) || 0;
              setAvailableSupply(unitMode === 'tons' ? raw * 1000 : raw);
            }}
            style={isExceedingCapacity ? { borderColor: '#D4B88A', background: 'var(--amber-pale)' } : {}}
          />
          {/* Storage & Fleet Transport Limit Reminder Tag */}
          <div style={{
            marginTop: '0.4rem',
            padding: '0.55rem 0.7rem',
            background: leftoverKg > 0 ? 'var(--amber-pale)' : 'var(--bg-base)',
            border: `1px solid ${leftoverKg > 0 ? '#D4B88A' : 'var(--beige-border)'}`,
            borderRadius: 'var(--radius-xs)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
              <span className="text-label-caps" style={{ fontSize: '0.62rem', color: leftoverKg > 0 ? 'var(--amber-warm)' : 'var(--text-faint)' }}>
                Leftover Supply (Surplus)
              </span>
              <span className="font-mono-data" style={{ fontSize: '0.75rem', fontWeight: 700, color: leftoverKg > 0 ? 'var(--amber-warm)' : 'var(--text-muted)' }}>
                {(leftoverKg / 1000).toFixed(1)} tons
              </span>
            </div>

            <p style={{ fontSize: '0.63rem', color: 'var(--text-muted)', margin: '0 0 0.45rem', lineHeight: '1.3' }}>
              {isSupplyLess
                ? `✨ Available supply (${(availableSupply / 1000).toFixed(1)}t) is 100% allocated across markets in exact demand ratio.`
                : leftoverKg > 0
                ? `📦 Supply (${(availableSupply / 1000).toFixed(1)}t) exceeds market demand (${(totalRawDemandKg / 1000).toFixed(1)}t). Leftover: ${(leftoverKg / 1000).toFixed(1)}t.`
                : `✅ All available supply (${(availableSupply / 1000).toFixed(1)}t) is fully allocated to market demand.`
              }
            </p>

            {/* Warehouse Storage Button (Phase 2 Integration) */}
            <button
              type="button"
              className="btn-secondary"
              onClick={() => onWarehouseStore && onWarehouseStore(leftoverKg)}
              style={{
                width: '100%',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem',
                padding: '0.45rem 0.6rem',
                fontSize: '0.68rem', fontWeight: 600,
                background: 'var(--bg-surface)',
                border: '1.5px solid var(--beige-border)',
                borderRadius: 'var(--radius-xs)',
                cursor: 'pointer',
              }}
            >
              <Warehouse size={13} color="var(--green-deep)" />
              Store Leftover in Warehouse (Phase 2)
            </button>
          </div>
        </div>

        {/* SP Slider */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
            <Label>Selling Price Markup (SP%)</Label>
            <span className="font-mono-data" style={{ fontSize: '0.72rem', color: 'var(--green-deep)', fontWeight: 500 }}>
              +{priceMarkup}% → ₹{effectivePricePerKg}/kg
            </span>
          </div>
          <input
            type="range" min="0" max="10" step="0.5"
            value={priceMarkup}
            onChange={e => setPriceMarkup(parseFloat(e.target.value))}
            style={{ width: '100%', accentColor: 'var(--green-deep)' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.25rem' }}>
            <span style={{ fontSize: '0.6rem', color: 'var(--text-faint)' }}>0% base</span>
            <span style={{ fontSize: '0.6rem', color: 'var(--text-faint)' }}>+5%</span>
            <span style={{ fontSize: '0.6rem', color: 'var(--text-faint)' }}>+10% max</span>
          </div>
        </div>
      </div>

      {/* ── PANEL 2: Action Buttons ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
        <button className="btn-secondary" onClick={onFetchForecast} disabled={loadingForecast}
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem', padding: '0.65rem' }}>
          <Sparkles size={13} style={{ flexShrink: 0, animation: loadingForecast ? 'spin 1s linear infinite' : 'none' }} />
          {loadingForecast ? 'Loading…' : `Fetch ${crop} Forecast`}
        </button>
        <button className="btn-secondary" onClick={onAllocate} disabled={allocating}
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem', padding: '0.65rem' }}>
          <Calculator size={13} style={{ flexShrink: 0 }} />
          {allocating ? 'Solving…' : 'Optimize Profit'}
        </button>
      </div>

      {/* ── PANEL 3: Market Demands Table ── */}
      <div className="panel" style={{ padding: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem', paddingBottom: '0.6rem', borderBottom: '1px solid var(--beige-border)' }}>
          <h2 className="font-display" style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-ink)', margin: 0 }}>
            Market Demands
          </h2>
          <div style={{ textAlign: 'right' }}>
            <span className="font-mono-data badge-neutral" style={{ fontSize: '0.65rem' }}>
              {(totalDemandKg / 1000).toFixed(1)}t allocated
            </span>
            {totalRawDemandKg > 0 && Math.abs(totalRawDemandKg - totalDemandKg) > 100 && (
              <span style={{ fontSize: '0.62rem', color: 'var(--text-faint)', marginLeft: '0.35rem' }}>
                (Mkt Cap: {(totalRawDemandKg / 1000).toFixed(1)}t)
              </span>
            )}
          </div>
        </div>

        {/* Column headers */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', padding: '0 0.5rem', marginBottom: '0.4rem' }}>
          <span className="text-label-caps" style={{ color: 'var(--text-faint)' }}>Market & ML Price</span>
          <span className="text-label-caps" style={{ color: 'var(--text-faint)', textAlign: 'right' }}>Routed Load ({unitMode})</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', maxHeight: '220px', overflowY: 'auto' }}>
          {locations.filter(loc => !loc.is_depot).map(loc => {
            const kgVal = demands[loc.name] ?? 0;
            const rawKg = rawDemands[loc.name] ?? kgVal;
            const hasDemand = kgVal > 0;
            const mlPrice = predictedPrices[loc.name];
            const markedUp = mlPrice ? (mlPrice * (1 + priceMarkup / 100)).toFixed(1) : null;
            const rawDisplay = unitMode === 'tons' ? (rawKg / 1000).toFixed(1) + 't' : rawKg.toLocaleString() + 'kg';

            return (
              <div key={loc.id} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '0.45rem 0.6rem',
                background: hasDemand ? 'var(--bg-raised)' : 'var(--bg-base)',
                border: `1px solid ${hasDemand ? 'var(--beige-border)' : 'transparent'}`,
                borderRadius: 'var(--radius-xs)',
              }}>
                {/* Left: location info + sideways market demand */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', minWidth: 0 }}>
                  <MapPin size={11} color={hasDemand ? 'var(--green-mid)' : 'var(--beige-mid)'} style={{ flexShrink: 0 }} />
                  <div style={{ minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexWrap: 'wrap' }}>
                      <p style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-ink)', margin: 0, whiteSpace: 'nowrap' }}>
                        {loc.name}
                      </p>
                      {markedUp && (
                        <span style={{
                          fontSize: '0.58rem', fontWeight: 700, fontFamily: 'DM Mono',
                          background: 'var(--green-pale)', color: 'var(--green-deep)',
                          border: '1px solid var(--green-light)',
                          borderRadius: 'var(--radius-xs)', padding: '0 0.25rem',
                        }}>₹{markedUp}/kg</span>
                      )}
                    </div>
                    {rawKg > 0 && (
                      <p style={{ fontSize: '0.62rem', color: 'var(--text-faint)', margin: '0.1rem 0 0', fontWeight: 500 }}>
                        Mkt Demand: <span style={{ fontWeight: 600, color: 'var(--text-body)' }}>{rawDisplay}</span>
                      </p>
                    )}
                  </div>
                </div>

                {/* Right: stepper */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', flexShrink: 0 }}>
                  <button className="btn-ghost" onClick={() => step(loc.name, -1)} style={{ padding: '0.2rem 0.4rem' }}>
                    <Minus size={10} />
                  </button>
                  <input
                    type="number" min="0"
                    step={unitMode === 'tons' ? '0.1' : '100'}
                    value={getDisplayVal(kgVal)}
                    onChange={e => handleInput(loc.name, e.target.value)}
                    style={{
                      width: 68, textAlign: 'center',
                      background: 'var(--bg-surface)',
                      border: '1.5px solid var(--beige-border)',
                      borderRadius: 'var(--radius-xs)',
                      color: 'var(--text-ink)',
                      fontFamily: 'DM Mono, monospace', fontSize: '0.75rem',
                      padding: '0.25rem 0.3rem', outline: 'none',
                    }}
                  />
                  <button className="btn-ghost" onClick={() => step(loc.name, 1)} style={{ padding: '0.2rem 0.4rem' }}>
                    <Plus size={10} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── PANEL 4: Action Buttons Row ── */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <button className="btn-secondary" onClick={onOptimizeRoutes} disabled={optimizing || totalDemandKg === 0}
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', padding: '0.7rem' }}>
          <Truck size={13} />
          Optimize Vehicle Routes (CVRP)
        </button>

        <button className="btn-primary" onClick={onMasterOptimize} disabled={optimizing}
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', padding: '0.85rem', fontSize: '0.82rem' }}>
          {optimizing
            ? <><RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> Optimizing {crop}…</>
            : <><span>Full End-to-End Optimization — {crop}</span><ChevronRight size={14} /></>
          }
        </button>
      </div>

    </div>
  );
}
