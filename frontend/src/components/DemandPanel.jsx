// frontend/src/components/DemandPanel.jsx
import React, { useState } from 'react';
import { Sparkles, MapPin, RefreshCw, ChevronRight, Plus, Minus, Edit3, TrendingUp, Calculator, Truck, DollarSign, ArrowUpRight } from 'lucide-react';

const CROPS = ['Wheat', 'Rice', 'Onion'];

// Realistic Pricing & Transportation Benchmarks per Crop in Delhi-NCR
const CROP_BENCHMARKS = {
  Wheat: {
    basePricePerKg: 34.0,
    priceRangeKg: '₹30 - ₹38 / kg',
    baseCostPerTon: 34000,
    bgColor: 'bg-amber-50 border-amber-200 text-amber-900',
    badgeColor: 'bg-amber-100 text-amber-800'
  },
  Onion: {
    basePricePerKg: 50.0, // Current real-world market price: ₹50/kg
    priceRangeKg: '₹46 - ₹55 / kg',
    baseCostPerTon: 50000,
    bgColor: 'bg-rose-50 border-rose-200 text-rose-900',
    badgeColor: 'bg-rose-100 text-rose-800'
  },
  Rice: {
    basePricePerKg: 48.0,
    priceRangeKg: '₹41 - ₹56 / kg',
    baseCostPerTon: 48000,
    bgColor: 'bg-emerald-50 border-emerald-200 text-emerald-900',
    badgeColor: 'bg-emerald-100 text-emerald-800'
  }
};

export default function DemandPanel({
  crop,
  setCrop,
  date,
  setDate,
  availableSupply,
  setAvailableSupply,
  priceMarkup,
  setPriceMarkup,
  coverageMode,
  setCoverageMode,
  demands,
  predictedPrices = {},
  onDemandChange,
  onFetchForecast,
  onAllocate,
  onOptimizeRoutes,
  onMasterOptimize,
  loadingForecast,
  allocating,
  optimizing,
  locations,
}) {
  const [unitMode, setUnitMode] = useState('tons');

  const totalDemandKg = Object.values(demands).reduce((acc, curr) => acc + (Number(curr) || 0), 0);
  const benchmark = CROP_BENCHMARKS[crop] || CROP_BENCHMARKS.Wheat;

  // Use ML-predicted average price if available, otherwise fall back to static base
  const priceVals = Object.values(predictedPrices).filter(v => v > 0);
  const mlAvgPricePerKg = priceVals.length > 0
    ? priceVals.reduce((a, b) => a + b, 0) / priceVals.length
    : benchmark.basePricePerKg;

  // Real-time effective price using ML-predicted price as base + SP markup %
  const effectivePricePerKg = (mlAvgPricePerKg * (1.0 + priceMarkup / 100.0)).toFixed(2);
  const effectiveCostPerTon = Math.round(mlAvgPricePerKg * 1000 * (1.0 + priceMarkup / 100.0));
  const markupGainPerTon = Math.round(effectiveCostPerTon - mlAvgPricePerKg * 1000);

  const getDisplayValue = (kgVal) => {
    if (unitMode === 'tons') {
      return (Number(kgVal || 0) / 1000).toString();
    }
    return (Number(kgVal || 0)).toString();
  };

  const handleInputChange = (locName, rawVal) => {
    const num = parseFloat(rawVal) || 0;
    const kgVal = unitMode === 'tons' ? Math.round(num * 1000) : Math.round(num);
    onDemandChange(locName, Math.max(0, kgVal));
  };

  const handleQuickStep = (locName, stepKg) => {
    const currentKg = demands[locName] || 0;
    const updated = Math.max(0, currentKg + stepKg);
    onDemandChange(locName, updated);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
      
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div className="flex items-center space-x-2">
          <Edit3 className="w-5 h-5 text-emerald-600" />
          <h2 className="font-bold text-slate-800 text-base">Farmer Inputs & Market Controls</h2>
        </div>
        
        {/* Unit Toggle */}
        <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200">
          <button
            type="button"
            onClick={() => setUnitMode('tons')}
            className={`px-2.5 py-1 text-xs font-semibold rounded-md transition ${
              unitMode === 'tons'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Tons (t)
          </button>
          <button
            type="button"
            onClick={() => setUnitMode('kg')}
            className={`px-2.5 py-1 text-xs font-semibold rounded-md transition ${
              unitMode === 'kg'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Kg
          </button>
        </div>
      </div>

      {/* Crop & Date Controls */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
            Selected Crop
          </label>
          <select
            value={crop}
            onChange={(e) => setCrop(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-2 text-xs font-bold text-slate-800 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
          >
            {CROPS.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
            Prediction Date
          </label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-2 text-xs font-semibold text-slate-800 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
          />
        </div>
      </div>

      {/* INLIST COST OF 1 TON & REALISTIC TRANSPORTATION COST BREAKDOWN */}
      <div className={`p-3.5 rounded-xl border text-xs space-y-2.5 transition ${benchmark.bgColor}`}>
        <div className="flex items-center justify-between font-bold">
          <span className="flex items-center space-x-1.5">
            <DollarSign className="w-4 h-4" />
            <span>Market Price & Transportation Freight Breakdown</span>
          </span>
          <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase ${benchmark.badgeColor}`}>
            {crop}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2 pt-1 border-t border-slate-200/50">
          <div className="bg-white/90 backdrop-blur-xs p-2.5 rounded-lg border border-slate-200/60 space-y-1">
            <span className="text-[10px] text-slate-500 font-semibold block uppercase">Cost of 1 Ton ({crop})</span>
            <p className="text-base font-black text-slate-900">
              ₹{effectiveCostPerTon.toLocaleString()} / Ton
            </p>
            <div className="flex items-center justify-between text-[10px] text-slate-600">
              <span>₹{effectivePricePerKg} / kg</span>
              {priceMarkup > 0 && (
                <span className="text-emerald-700 font-bold flex items-center">
                  <ArrowUpRight className="w-3 h-3 inline" />+₹{markupGainPerTon.toLocaleString()}/t
                </span>
              )}
            </div>
          </div>

          <div className="bg-white/90 backdrop-blur-xs p-2.5 rounded-lg border border-slate-200/60 space-y-1">
            <span className="text-[10px] text-slate-500 font-semibold block uppercase">Transportation Cost / Unit</span>
            <p className="text-base font-black text-slate-900">
              ₹100.00 / km
            </p>
            <span className="text-[10px] text-slate-600 block">
              ₹10.00 per Ton / km (Freight rate)
            </span>
          </div>
        </div>
      </div>

      {/* Available Supply & Real-time Selling Price (SP) Slider */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold text-slate-700 flex items-center space-x-1.5">
            <TrendingUp className="w-4 h-4 text-emerald-600" />
            <span>Total Available Crop Supply</span>
          </label>
          <span className="text-xs font-extrabold text-emerald-700">
            {(availableSupply / 1000).toFixed(1)} Tons ({availableSupply.toLocaleString()} kg)
          </span>
        </div>
        <input
          type="number"
          min="1000"
          step="1000"
          value={unitMode === 'tons' ? availableSupply / 1000 : availableSupply}
          onChange={(e) => {
            const raw = parseFloat(e.target.value) || 0;
            setAvailableSupply(unitMode === 'tons' ? raw * 1000 : raw);
          }}
          className="w-full bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-xs font-bold text-slate-800 focus:ring-2 focus:ring-emerald-500"
        />

        {/* Real-time Selling Price (SP) Adjustment Slider */}
        <div className="space-y-1.5 pt-1">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
            <span>Selling Price (SP) Adjustment:</span>
            <span className="font-extrabold text-emerald-600 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded text-xs">
              +{priceMarkup}% (₹{effectivePricePerKg}/kg)
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="10"
            step="0.5"
            value={priceMarkup}
            onChange={(e) => setPriceMarkup(parseFloat(e.target.value))}
            className="w-full accent-emerald-600 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-400 font-bold">
            <span>0% (Base ₹{benchmark.basePricePerKg}/kg)</span>
            <span>+5% (₹{(benchmark.basePricePerKg * 1.05).toFixed(1)}/kg)</span>
            <span>+10% Cap (₹{(benchmark.basePricePerKg * 1.1).toFixed(1)}/kg)</span>
          </div>
        </div>
      </div>

      {/* AI Action Buttons */}
      <div className="grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={onFetchForecast}
          disabled={loadingForecast}
          className="flex items-center justify-center space-x-1.5 bg-emerald-50 hover:bg-emerald-100 border border-emerald-300 text-emerald-800 font-bold py-2.5 px-2 rounded-lg text-xs transition disabled:opacity-50 shadow-2xs"
        >
          <Sparkles className={`w-3.5 h-3.5 text-emerald-600 ${loadingForecast ? 'animate-spin' : ''}`} />
          <span>{loadingForecast ? 'Loading...' : `Fetch ${crop} Forecast`}</span>
        </button>

        <button
          type="button"
          onClick={onAllocate}
          disabled={allocating}
          className="flex items-center justify-center space-x-1.5 bg-blue-50 hover:bg-blue-100 border border-blue-300 text-blue-800 font-bold py-2.5 px-2 rounded-lg text-xs transition disabled:opacity-50 shadow-2xs"
        >
          <Calculator className={`w-3.5 h-3.5 text-blue-600 ${allocating ? 'animate-spin' : ''}`} />
          <span>{allocating ? 'Solving...' : 'Optimize Profit'}</span>
        </button>
      </div>

      {/* Market Quantities Input / Edit Table */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs font-bold text-slate-500 px-1 border-b pb-1">
          <span>Destination Market</span>
          <span>Demands ({unitMode})</span>
        </div>

        <div className="max-h-52 overflow-y-auto space-y-2 pr-1 divide-y divide-slate-100">
          {locations
            .filter((loc) => !loc.is_depot)
            .map((loc) => {
              const currentDemandKg = demands[loc.name] ?? 0;
              const hasDemand = currentDemandKg > 0;
              const stepVal = unitMode === 'tons' ? 1000 : 500;
              const mlPrice = predictedPrices[loc.name];
              const markedUpPrice = mlPrice ? (mlPrice * (1.0 + priceMarkup / 100.0)).toFixed(2) : null;

              return (
                <div
                  key={loc.id}
                  className={`pt-2 flex items-center justify-between p-2 rounded-lg transition border ${
                    hasDemand
                      ? 'bg-emerald-50/40 border-emerald-200/80 shadow-2xs'
                      : 'bg-slate-50/60 border-slate-200/60 opacity-75'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <MapPin className={`w-4 h-4 shrink-0 ${hasDemand ? 'text-emerald-600' : 'text-slate-400'}`} />
                    <div>
                      <p className="text-xs font-bold text-slate-800">{loc.name}</p>
                      <div className="flex items-center space-x-1">
                        <span className="text-[10px] text-slate-500">
                          {hasDemand ? `${(currentDemandKg / 1000).toFixed(1)}t` : '0kg'}
                        </span>
                        {markedUpPrice && (
                          <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-1 rounded">
                            ₹{markedUpPrice}/kg
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-1.5">
                    <button
                      type="button"
                      onClick={() => handleQuickStep(loc.name, -stepVal)}
                      className="w-6 h-6 flex items-center justify-center rounded bg-white border border-slate-200 text-slate-600 hover:bg-slate-100 text-xs font-bold shadow-2xs"
                    >
                      <Minus className="w-3 h-3" />
                    </button>

                    <input
                      type="number"
                      min="0"
                      step={unitMode === 'tons' ? '0.1' : '100'}
                      value={getDisplayValue(currentDemandKg)}
                      onChange={(e) => handleInputChange(loc.name, e.target.value)}
                      className="w-20 bg-white border border-slate-300 rounded px-2 py-1 text-center text-xs font-bold text-slate-800 focus:ring-2 focus:ring-emerald-500 shadow-2xs"
                    />

                    <button
                      type="button"
                      onClick={() => handleQuickStep(loc.name, stepVal)}
                      className="w-6 h-6 flex items-center justify-center rounded bg-white border border-slate-200 text-slate-600 hover:bg-slate-100 text-xs font-bold shadow-2xs"
                    >
                      <Plus className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="space-y-2 pt-1">
        <button
          type="button"
          onClick={onOptimizeRoutes}
          disabled={optimizing || totalDemandKg === 0}
          className="w-full flex items-center justify-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2.5 px-4 rounded-xl text-xs transition shadow-sm disabled:opacity-50"
        >
          <Truck className={`w-4 h-4 ${optimizing ? 'animate-spin' : ''}`} />
          <span>Optimize Vehicle Routes (CVRP)</span>
        </button>

        <button
          type="button"
          onClick={onMasterOptimize}
          disabled={optimizing}
          className="w-full flex items-center justify-center space-x-2 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold py-3 px-4 rounded-xl text-sm transition shadow-md hover:shadow-lg disabled:opacity-50"
        >
          {optimizing ? (
            <>
              <RefreshCw className="w-5 h-5 animate-spin" />
              <span>Optimizing {crop} Logistics...</span>
            </>
          ) : (
            <>
              <span>Run Full End-to-End Optimization ({crop})</span>
              <ChevronRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>

    </div>
  );
}
