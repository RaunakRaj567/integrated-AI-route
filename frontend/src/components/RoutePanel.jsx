// frontend/src/components/RoutePanel.jsx
import React from 'react';
import { Navigation, ArrowRight, Truck } from 'lucide-react';
import { getVehicleColor } from './MapView';

export default function RoutePanel({ optimizationResult, selectedVehicleId, onSelectVehicle }) {
  if (!optimizationResult) {
    return (
      <div style={{
        background: 'var(--bg-surface)',
        border: '1.5px dashed var(--beige-border)',
        borderRadius: 'var(--radius-md)',
        padding: '2.5rem 1.5rem',
        textAlign: 'center',
      }}>
        <Navigation size={28} color="var(--beige-mid)" style={{ margin: '0 auto 0.75rem' }} />
        <h3 className="font-display" style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-body)', margin: '0 0 0.4rem' }}>
          No Routes Calculated Yet
        </h3>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-faint)', maxWidth: 320, margin: '0 auto' }}>
          Run <strong style={{ color: 'var(--green-deep)' }}>Optimize Vehicle Routes</strong> or{' '}
          <strong style={{ color: 'var(--green-deep)' }}>Full End-to-End Optimization</strong> to generate schedules.
        </p>
      </div>
    );
  }

  const summary = optimizationResult.summary || optimizationResult.routing_summary || {};
  const routes = optimizationResult.routes || [];
  const totalDemandKg = summary.total_load_kg || summary.total_demand_kg || 0;
  const vehiclesUsed = summary.vehicles_used || routes.length || 0;
  const vehiclesAvailable = summary.vehicles_available || 5;

  const fmt = (mins = 0) => {
    const h = Math.floor(mins / 60);
    const m = Math.round(mins % 60);
    return h > 0 ? `${h}h ${m}m` : `${m}m`;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>

      {/* ── Summary strip ── */}
      <div className="panel" style={{ padding: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
          <span className="text-label-caps" style={{ color: 'var(--text-muted)' }}>Logistics & Fleet Summary</span>
          <span className="badge-green">{vehiclesUsed} deployed · {Math.max(0, vehiclesAvailable - vehiclesUsed)} standby</span>
        </div>

        {/* 4 metrics in a tight row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.6rem' }}>
          {[
            { label: 'Cargo Delivered', val: `${(totalDemandKg / 1000).toFixed(1)}`, unit: 'tons', sub: `${totalDemandKg.toLocaleString()} kg` },
            { label: 'Road Distance', val: `${summary.total_distance_km || 0}`, unit: 'km', sub: 'all routes combined' },
            { label: 'Travel Time', val: fmt(summary.total_duration_minutes || 0), unit: '', sub: 'est. driving' },
            { label: 'Fleet Usage', val: `${vehiclesUsed}/${vehiclesAvailable}`, unit: 'trucks', sub: `${summary.fleet_utilization_percent || ((vehiclesUsed / vehiclesAvailable) * 100).toFixed(0)}% utilization` },
          ].map(({ label, val, unit, sub }) => (
            <div key={label} style={{
              background: 'var(--bg-base)',
              border: '1px solid var(--beige-border)',
              borderRadius: 'var(--radius-xs)',
              padding: '0.65rem 0.75rem',
            }}>
              <p className="text-label-caps" style={{ color: 'var(--text-faint)', margin: '0 0 0.25rem' }}>{label}</p>
              <p className="font-mono-data" style={{ fontSize: '1.15rem', fontWeight: 500, color: 'var(--text-ink)', margin: 0 }}>
                {val} <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{unit}</span>
              </p>
              <p style={{ fontSize: '0.62rem', color: 'var(--text-faint)', margin: '0.15rem 0 0' }}>{sub}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Route Cards ── */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem', padding: '0 0.1rem' }}>
          <span className="text-label-caps" style={{ color: 'var(--text-muted)' }}>
            Optimized Schedules — {routes.length} active routes
          </span>
          <span style={{ fontSize: '0.65rem', color: 'var(--text-faint)' }}>click to highlight on map</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
          {routes.map((route) => {
            const isSelected = selectedVehicleId === route.vehicle_id;
            const routeColor = getVehicleColor(route.vehicle_id);
            const capacityKg = route.vehicle_capacity_kg || route.capacity_kg || 20000;
            const loadKg = route.load_kg || 0;
            const utilization = route.utilization_percent || 0;
            const stopNames = route.route_names || route.route || ['Delhi', 'Delhi'];

            return (
              <div
                key={route.vehicle_id}
                className="route-card"
                onClick={() => onSelectVehicle(isSelected ? null : route.vehicle_id)}
                style={isSelected ? {
                  borderColor: routeColor,
                  background: 'var(--bg-raised)',
                  borderLeftWidth: '4px',
                } : { borderLeftWidth: '4px', borderLeftColor: `${routeColor}55` }}
              >
                {/* Card Header */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <div style={{
                      width: 10, height: 10, borderRadius: '50%',
                      background: routeColor, flexShrink: 0,
                    }} />
                    <h4 className="font-display" style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-ink)', margin: 0 }}>
                      Truck {route.vehicle_id}
                    </h4>
                    <span className="badge-neutral">{(capacityKg / 1000).toFixed(0)}t cap</span>
                  </div>
                  <div style={{ display: 'flex', gap: '1rem' }}>
                    <span className="font-mono-data" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      {route.distance_km || 0} km
                    </span>
                    <span className="font-mono-data" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      {fmt(route.duration_minutes || 0)}
                    </span>
                  </div>
                </div>

                {/* Progress */}
                <div style={{ marginBottom: '0.65rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                    <span className="font-mono-data" style={{ fontSize: '0.7rem', color: 'var(--text-body)' }}>
                      {loadKg.toLocaleString()} kg &nbsp;·&nbsp; {(loadKg / 1000).toFixed(1)}t / {(capacityKg / 1000).toFixed(0)}t
                    </span>
                    <span className="font-mono-data" style={{
                      fontSize: '0.7rem', fontWeight: 500,
                      color: utilization > 85 ? 'var(--green-deep)' : 'var(--amber-warm)',
                    }}>
                      {utilization}%
                    </span>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill" style={{ width: `${Math.min(100, utilization)}%`, background: routeColor }} />
                  </div>
                </div>

                {/* Stop Sequence */}
                <div style={{
                  background: 'var(--bg-base)',
                  border: '1px solid var(--beige-border)',
                  borderRadius: 'var(--radius-xs)',
                  padding: '0.45rem 0.65rem',
                  display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.3rem',
                }}>
                  <span className="text-label-caps" style={{ color: 'var(--text-faint)', marginRight: '0.2rem' }}>path:</span>
                  {stopNames.map((name, i) => (
                    <React.Fragment key={i}>
                      <span style={{
                        fontSize: '0.68rem', fontWeight: 700,
                        padding: '0.1rem 0.4rem',
                        background: (i === 0 || i === stopNames.length - 1) ? 'var(--green-pale)' : 'var(--bg-raised)',
                        color: (i === 0 || i === stopNames.length - 1) ? 'var(--green-deep)' : 'var(--text-body)',
                        border: `1px solid ${(i === 0 || i === stopNames.length - 1) ? 'var(--green-light)' : 'var(--beige-border)'}`,
                        borderRadius: 'var(--radius-xs)',
                      }}>{name}</span>
                      {i < stopNames.length - 1 && (
                        <ArrowRight size={11} color="var(--beige-mid)" style={{ flexShrink: 0 }} />
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
