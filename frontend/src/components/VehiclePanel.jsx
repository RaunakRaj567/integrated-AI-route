// frontend/src/components/VehiclePanel.jsx
import React from 'react';
import { Truck, CheckCircle2, ShieldAlert } from 'lucide-react';
import { getVehicleColor } from './MapView';

export default function VehiclePanel({
  vehicleCapacities = [],
  totalDemand = 0,
  routes = [],
}) {
  const totalFleetCapacity = vehicleCapacities.reduce((a, b) => a + b, 0);
  const isCapacitySufficient = totalFleetCapacity >= totalDemand;
  const activeVehicleIds = new Set((routes || []).map((r) => r.vehicle_id));

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
      
      {/* Title */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div className="flex items-center space-x-2">
          <Truck className="w-5 h-5 text-emerald-600" />
          <h2 className="font-bold text-slate-800 text-base">Fleet Inventory</h2>
        </div>
        <span className="text-xs bg-slate-100 text-slate-700 font-bold px-2 py-0.5 rounded">
          {vehicleCapacities.length} Trucks Available
        </span>
      </div>

      {/* Fleet Summary Indicator */}
      <div
        className={`p-3 rounded-lg border flex items-start space-x-2.5 text-xs ${
          isCapacitySufficient
            ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900'
            : 'bg-rose-50 border-rose-200 text-rose-900'
        }`}
      >
        {isCapacitySufficient ? (
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
        ) : (
          <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
        )}
        <div>
          <span className="font-bold">
            {isCapacitySufficient
              ? 'Fleet capacity is sufficient'
              : 'Capacity Alert: Total Demand exceeds Fleet Capacity!'}
          </span>
          <p className="text-slate-600 mt-0.5">
            Total Fleet: <strong className="text-slate-900">{(totalFleetCapacity / 1000).toFixed(1)} tons</strong> |
            Demand: <strong className="text-slate-900">{(totalDemand / 1000).toFixed(1)} tons</strong>
          </p>
        </div>
      </div>

      {/* Vehicle Capacities List */}
      <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
        {vehicleCapacities.map((cap, idx) => {
          const vehicleId = idx + 1;
          const isDeployed = activeVehicleIds.has(vehicleId);
          const color = getVehicleColor(vehicleId);
          const assignedRoute = (routes || []).find((r) => r.vehicle_id === vehicleId);
          const loadKg = assignedRoute?.load_kg || 0;

          return (
            <div
              key={idx}
              className={`flex items-center justify-between p-2.5 rounded-lg border transition ${
                isDeployed
                  ? 'bg-white border-slate-300 shadow-2xs ring-1 ring-slate-200'
                  : 'bg-slate-50/60 border-slate-100 opacity-60'
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <span
                  className="w-6 h-6 rounded-full text-white text-xs font-black flex items-center justify-center shadow-2xs"
                  style={{ backgroundColor: isDeployed ? color : '#94a3b8' }}
                >
                  {vehicleId}
                </span>
                <div>
                  <span className="text-xs font-bold text-slate-800">Vehicle {vehicleId}</span>
                  <span className="text-[10px] text-slate-500 block">
                    {(cap / 1000).toFixed(0)}-Ton Capacity ({cap.toLocaleString()} kg)
                  </span>
                </div>
              </div>

              <div className="text-right">
                {isDeployed ? (
                  <span
                    className="text-[11px] font-extrabold px-2 py-0.5 rounded-full"
                    style={{ backgroundColor: `${color}18`, color: color }}
                  >
                    Deployed ({(loadKg / 1000).toFixed(1)}t)
                  </span>
                ) : (
                  <span className="text-[10px] font-semibold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                    Standby (Unused)
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}
