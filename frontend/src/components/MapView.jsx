// frontend/src/components/MapView.jsx
import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';

// Distinct color palette for up to 10+ vehicle routes
export const ROUTE_COLORS = {
  1: '#2563eb', // Truck 1: Royal Blue
  2: '#7c3aed', // Truck 2: Purple / Violet
  3: '#059669', // Truck 3: Emerald Green
  4: '#ea580c', // Truck 4: Bright Orange
  5: '#e11d48', // Truck 5: Crimson Red
  6: '#0891b2', // Truck 6: Cyan
  7: '#d97706', // Truck 7: Amber Gold
  8: '#4f46e5', // Truck 8: Indigo
  9: '#db2777', // Truck 9: Pink Magenta
  10: '#0d9488',// Truck 10: Dark Teal
};

export function getVehicleColor(vehicleId) {
  return ROUTE_COLORS[vehicleId] || ROUTE_COLORS[((vehicleId - 1) % 10) + 1] || '#2563eb';
}

// Helper to auto-fit map view to markers and routes
function MapBoundsUpdater({ locations, routes, activeVehicleId }) {
  const map = useMap();

  useEffect(() => {
    if (!locations || locations.length === 0) return;

    if (activeVehicleId && routes && routes.length > 0) {
      const activeRoute = routes.find((r) => r.vehicle_id === activeVehicleId);
      if (activeRoute && activeRoute.route_nodes) {
        const routeCoords = activeRoute.route_nodes.map((nodeIdx) => {
          const loc = locations[nodeIdx];
          return [loc.latitude, loc.longitude];
        });
        if (routeCoords.length > 0) {
          map.fitBounds(L.latLngBounds(routeCoords), { padding: [50, 50] });
          return;
        }
      }
    }

    const bounds = L.latLngBounds(locations.map((loc) => [loc.latitude, loc.longitude]));
    map.fitBounds(bounds, { padding: [40, 40] });
  }, [locations, routes, activeVehicleId, map]);

  return null;
}

export default function MapView({
  locations = [],
  demands = {},
  routes = [],
  selectedVehicleId = null,
  onSelectVehicle = () => {},
}) {
  const defaultCenter = [28.6139, 77.2090];

  const createCustomIcon = (isDepot, demandKg) => {
    if (isDepot) {
      return L.divIcon({
        className: 'custom-pin',
        html: `
          <div style="background-color: #dc2626; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.4); font-size: 18px;">
            🏬
          </div>
        `,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
      });
    }

    const hasDemand = demandKg > 0;
    const bgColor = hasDemand ? '#16a34a' : '#94a3b8';
    const text = hasDemand ? `${(demandKg / 1000).toFixed(1)}t` : '0';

    return L.divIcon({
      className: 'custom-pin',
      html: `
        <div style="background-color: ${bgColor}; color: white; padding: 2px 7px; border-radius: 12px; font-weight: 800; border: 2px solid white; box-shadow: 0 3px 6px rgba(0,0,0,0.3); font-size: 11px; white-space: nowrap;">
          ${text}
        </div>
      `,
      iconSize: [42, 22],
      iconAnchor: [21, 11],
    });
  };

  const extractPolylinePositions = (route) => {
    if (!route.geojson || !route.geojson.coordinates) {
      return (route.route_nodes || []).map((nodeIdx) => [
        locations[nodeIdx]?.latitude || 28.6,
        locations[nodeIdx]?.longitude || 77.2,
      ]);
    }
    return route.geojson.coordinates.map(([lon, lat]) => [lat, lon]);
  };

  return (
    <div className="relative w-full h-[560px] bg-slate-100 rounded-xl overflow-hidden border border-slate-200 shadow-sm flex flex-col">
      
      {/* Top Route Selector Ribbon */}
      {routes.length > 0 && (
        <div className="bg-white/95 backdrop-blur-sm border-b border-slate-200 px-3 py-2 flex items-center justify-between z-20 overflow-x-auto gap-2">
          <div className="flex items-center space-x-1.5 shrink-0">
            <span className="text-xs font-bold text-slate-600">Truck Routes:</span>
            <button
              type="button"
              onClick={() => onSelectVehicle(null)}
              className={`px-2.5 py-1 rounded-md text-xs font-bold transition ${
                selectedVehicleId === null
                  ? 'bg-slate-800 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Show All ({routes.length} Trucks)
            </button>
          </div>

          <div className="flex items-center space-x-1.5 overflow-x-auto pb-0.5">
            {routes.map((route) => {
              const isSelected = selectedVehicleId === route.vehicle_id;
              const color = getVehicleColor(route.vehicle_id);

              return (
                <button
                  key={route.vehicle_id}
                  type="button"
                  onClick={() => onSelectVehicle(isSelected ? null : route.vehicle_id)}
                  style={{
                    backgroundColor: isSelected ? color : undefined,
                    borderColor: color,
                    color: isSelected ? '#ffffff' : color,
                  }}
                  className={`px-2.5 py-1 rounded-md text-xs font-bold border transition flex items-center space-x-1.5 shrink-0 shadow-2xs ${
                    isSelected ? 'shadow-sm' : 'bg-white hover:bg-slate-50'
                  }`}
                >
                  <span
                    className="w-2.5 h-2.5 rounded-full inline-block"
                    style={{ backgroundColor: isSelected ? '#ffffff' : color }}
                  />
                  <span>Truck {route.vehicle_id}</span>
                  <span className="opacity-80 text-[10px]">
                    ({(route.load_kg / 1000).toFixed(1)}t)
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Map Container */}
      <div className="relative flex-1 w-full h-full">
        <MapContainer
          center={defaultCenter}
          zoom={9}
          scrollWheelZoom={true}
          className="w-full h-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <MapBoundsUpdater
            locations={locations}
            routes={routes}
            activeVehicleId={selectedVehicleId}
          />

          {/* Location Markers */}
          {locations.map((loc) => {
            const isDepot = loc.is_depot;
            const demand = demands[loc.name] || 0;
            return (
              <Marker
                key={loc.id}
                position={[loc.latitude, loc.longitude]}
                icon={createCustomIcon(isDepot, demand)}
              >
                <Popup>
                  <div className="text-xs space-y-1 p-0.5 font-sans">
                    <div className="font-bold text-slate-900 text-sm border-b pb-1">
                      {loc.name} {isDepot ? '(Delhi Central Depot)' : ''}
                    </div>
                    <div className="text-slate-700">
                      <span className="font-semibold">Demand:</span>{' '}
                      {isDepot ? 'Depot Collection Hub' : `${demand.toLocaleString()} kg (${(demand / 1000).toFixed(1)} tons)`}
                    </div>
                    <div className="text-slate-700">
                      <span className="font-semibold">Status:</span>{' '}
                      {isDepot ? (
                        <span className="text-amber-600 font-bold">Central Depot</span>
                      ) : demand > 0 ? (
                        <span className="text-emerald-700 font-bold">Active Market Delivery</span>
                      ) : (
                        <span className="text-slate-400 font-medium">0 Demand</span>
                      )}
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}

          {/* Render Route Polylines */}
          {routes.map((route) => {
            const positions = extractPolylinePositions(route);
            if (positions.length === 0) return null;

            const color = getVehicleColor(route.vehicle_id);
            const isSelected = selectedVehicleId === route.vehicle_id;
            const isDimmed = selectedVehicleId !== null && !isSelected;

            return (
              <React.Fragment key={`route-poly-${route.vehicle_id}`}>
                {/* Glow layer when selected */}
                {isSelected && (
                  <Polyline
                    positions={positions}
                    pathOptions={{
                      color: color,
                      weight: 12,
                      opacity: 0.35,
                      lineCap: 'round',
                    }}
                  />
                )}

                {/* Main road polyline */}
                <Polyline
                  positions={positions}
                  eventHandlers={{
                    click: () => onSelectVehicle(isSelected ? null : route.vehicle_id),
                  }}
                  pathOptions={{
                    color: color,
                    weight: isSelected ? 6 : isDimmed ? 3 : 5,
                    opacity: isDimmed ? 0.25 : isSelected ? 1.0 : 0.9,
                    lineCap: 'round',
                    lineJoin: 'round',
                  }}
                >
                  <Tooltip sticky>
                    <div className="text-xs font-sans">
                      <div className="font-bold text-slate-900">
                        Truck {route.vehicle_id} ({route.distance_km} km)
                      </div>
                      <div className="text-slate-600">
                        Route: {route.route_names ? route.route_names.join(' → ') : route.route_path_string}
                      </div>
                      <div className="text-emerald-700 font-semibold">
                        Cargo: {route.load_kg.toLocaleString()} kg / {route.vehicle_capacity_kg.toLocaleString()} kg ({route.utilization_percent}%)
                      </div>
                    </div>
                  </Tooltip>
                </Polyline>
              </React.Fragment>
            );
          })}
        </MapContainer>

        {/* Floating Map Legend */}
        <div className="absolute bottom-3 right-3 z-[1000] bg-white/95 backdrop-blur-sm border border-slate-200 rounded-lg p-2.5 shadow-md text-xs space-y-1.5 pointer-events-auto max-w-[220px] max-h-48 overflow-y-auto">
          <div className="font-bold text-slate-800 border-b border-slate-200 pb-1 flex items-center justify-between sticky top-0 bg-white">
            <span>Route Map Legend</span>
            {selectedVehicleId && (
              <button
                type="button"
                onClick={() => onSelectVehicle(null)}
                className="text-[10px] text-blue-600 font-bold hover:underline"
              >
                Reset Filter
              </button>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-4 h-4 rounded-full bg-red-600 flex items-center justify-center text-[10px] text-white font-bold">🏬</span>
            <span className="text-slate-700">Delhi Depot</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-3.5 h-3.5 rounded bg-emerald-600"></span>
            <span className="text-slate-700">Delivery Market</span>
          </div>
          {routes.map((route) => (
            <div key={route.vehicle_id} className="flex items-center space-x-2">
              <span
                className="w-3.5 h-1.5 rounded-full shrink-0"
                style={{ backgroundColor: getVehicleColor(route.vehicle_id) }}
              />
              <span className="text-slate-700 font-medium truncate">
                Truck {route.vehicle_id} ({(route.load_kg/1000).toFixed(1)}t)
              </span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
