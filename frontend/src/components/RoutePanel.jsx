// frontend/src/components/RoutePanel.jsx
import React from 'react';
import { Truck, Navigation, Gauge, Clock, ArrowRight, CheckCircle2 } from 'lucide-react';
import { getVehicleColor } from './MapView';

export default function RoutePanel({
  optimizationResult,
  selectedVehicleId,
  onSelectVehicle,
}) {
  if (!optimizationResult) {
    return (
      <div className="bg-white rounded-xl border border-dashed border-slate-300 p-8 text-center space-y-3">
        <Navigation className="w-10 h-10 text-slate-300 mx-auto" />
        <h3 className="text-slate-700 font-bold text-sm">No Delivery Routes Calculated Yet</h3>
        <p className="text-xs text-slate-500 max-w-sm mx-auto">
          Click <span className="font-bold text-emerald-600">"Optimize Vehicle Routes (CVRP)"</span> or <span className="font-bold text-emerald-600">"Run Full End-to-End Optimization"</span> to generate vehicle assignments.
        </p>
      </div>
    );
  }

  // Handle both { summary, routes } and { routing_summary, routes } formats safely
  const summary = optimizationResult.summary || optimizationResult.routing_summary || {};
  const routes = optimizationResult.routes || [];

  const formatDuration = (mins = 0) => {
    const hours = Math.floor(mins / 60);
    const remainingMins = Math.round(mins % 60);
    if (hours > 0) {
      return `${hours}h ${remainingMins}m`;
    }
    return `${remainingMins} min`;
  };

  const totalDemandKg = summary.total_load_kg || summary.total_demand_kg || 0;
  const vehiclesUsed = summary.vehicles_used || routes.length || 0;
  const vehiclesAvailable = summary.vehicles_available || 5;

  return (
    <div className="space-y-4">
      
      {/* 1. Summary Cards Header */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-2 mb-3">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Logistics & Fleet Summary
          </h3>
          <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
            {vehiclesUsed} Trucks Deployed ({Math.max(0, vehiclesAvailable - vehiclesUsed)} Standby)
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          
          <div className="bg-slate-50 border border-slate-100 rounded-lg p-3">
            <span className="text-[11px] text-slate-500 font-medium">Total Cargo Delivered</span>
            <p className="text-lg font-black text-slate-900 mt-0.5">
              {(totalDemandKg / 1000).toFixed(1)}{' '}
              <span className="text-xs font-normal text-slate-500">tons</span>
            </p>
            <span className="text-[10px] text-slate-400 font-medium">
              {totalDemandKg.toLocaleString()} kg
            </span>
          </div>

          <div className="bg-slate-50 border border-slate-100 rounded-lg p-3">
            <span className="text-[11px] text-slate-500 font-medium">Total Road Distance</span>
            <p className="text-lg font-black text-slate-900 mt-0.5">
              {summary.total_distance_km || 0}{' '}
              <span className="text-xs font-normal text-slate-500">km</span>
            </p>
            <span className="text-[10px] text-slate-400 font-medium">Across all truck routes</span>
          </div>

          <div className="bg-slate-50 border border-slate-100 rounded-lg p-3">
            <span className="text-[11px] text-slate-500 font-medium">Total Travel Time</span>
            <p className="text-lg font-black text-slate-900 mt-0.5">
              {formatDuration(summary.total_duration_minutes || 0)}
            </p>
            <span className="text-[10px] text-slate-400 font-medium">Estimated driving</span>
          </div>

          <div className="bg-slate-50 border border-slate-100 rounded-lg p-3">
            <span className="text-[11px] text-slate-500 font-medium">Fleet Utilization</span>
            <p className="text-lg font-black text-emerald-600 mt-0.5">
              {vehiclesUsed} / {vehiclesAvailable}{' '}
              <span className="text-xs font-normal text-slate-500 font-bold">trucks</span>
            </p>
            <span className="text-[10px] text-slate-400 font-medium">
              {summary.fleet_utilization_percent || ((vehiclesUsed / vehiclesAvailable) * 100).toFixed(0)}% load index
            </span>
          </div>

        </div>
      </div>

      {/* 2. Route Cards List */}
      <div className="space-y-3">
        <div className="flex items-center justify-between px-1">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Optimized Vehicle Schedules ({routes.length} Active Routes)
          </h3>
          <span className="text-xs text-slate-500 font-medium">
            Click any card to highlight on map
          </span>
        </div>

        {routes.map((route) => {
          const isSelected = selectedVehicleId === route.vehicle_id;
          const routeColor = getVehicleColor(route.vehicle_id);
          const capacityKg = route.vehicle_capacity_kg || route.capacity_kg || 20000;
          const loadKg = route.load_kg || 0;
          const utilization = route.utilization_percent || 0;
          const stopNames = route.route_names || route.route || ["Delhi", "Delhi"];

          return (
            <div
              key={route.vehicle_id}
              onClick={() => onSelectVehicle(isSelected ? null : route.vehicle_id)}
              className={`cursor-pointer bg-white rounded-xl border transition-all p-4 space-y-3 shadow-sm hover:shadow-md ${
                isSelected
                  ? 'border-blue-500 ring-2 ring-blue-200'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              {/* Card Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div
                    className="w-4 h-4 rounded-full shadow-2xs"
                    style={{ backgroundColor: routeColor }}
                  />
                  <div>
                    <h4 className="font-black text-slate-900 text-sm flex items-center space-x-2">
                      <span>Truck {route.vehicle_id}</span>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                        {(capacityKg / 1000).toFixed(0)}-Ton Capacity
                      </span>
                    </h4>
                  </div>
                </div>

                <div className="flex items-center space-x-3 text-xs">
                  <span className="text-slate-700">
                    Distance: <strong className="text-slate-900">{route.distance_km || 0} km</strong>
                  </span>
                  <span className="text-slate-300">•</span>
                  <span className="text-slate-700">
                    Est. Time: <strong className="text-slate-900">{formatDuration(route.duration_minutes || 0)}</strong>
                  </span>
                </div>
              </div>

              {/* Payload & Capacity Progress Bar */}
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-600 font-medium">
                    Payload: <strong className="text-slate-900">{loadKg.toLocaleString()} kg</strong> ({(loadKg / 1000).toFixed(1)}t) / {(capacityKg / 1000).toFixed(0)}t Cap
                  </span>
                  <span
                    className="font-bold"
                    style={{ color: utilization > 85 ? '#16a34a' : '#d97706' }}
                  >
                    {utilization}% Capacity Utilization
                  </span>
                </div>
                <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden border border-slate-200">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${Math.min(100, utilization)}%`,
                      backgroundColor: routeColor,
                    }}
                  />
                </div>
              </div>

              {/* Stop Sequence */}
              <div className="bg-slate-50 rounded-lg p-2.5 flex items-center flex-wrap gap-1.5 text-xs text-slate-700 border border-slate-100">
                <span className="text-[11px] font-bold text-slate-400 mr-1">Route Path:</span>
                {stopNames.map((stopName, sIdx) => (
                  <React.Fragment key={sIdx}>
                    <span
                      className={`px-2 py-0.5 rounded font-bold ${
                        sIdx === 0 || sIdx === stopNames.length - 1
                          ? 'bg-red-100 text-red-800 border border-red-200'
                          : 'bg-white text-slate-800 border border-slate-200 shadow-2xs'
                      }`}
                    >
                      {stopName}
                    </span>
                    {sIdx < stopNames.length - 1 && (
                      <ArrowRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    )}
                  </React.Fragment>
                ))}
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
}
