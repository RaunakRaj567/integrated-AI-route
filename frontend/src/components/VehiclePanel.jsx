// frontend/src/components/VehiclePanel.jsx
import React from 'react';
import { Truck, CheckCircle2, ShieldAlert } from 'lucide-react';
import { getVehicleColor } from './MapView';

export default function VehiclePanel({ vehicleCapacities = [], totalDemand = 0, routes = [] }) {
  const totalFleetCapacity = vehicleCapacities.reduce((a, b) => a + b, 0);
  const isCapacitySufficient = totalFleetCapacity >= totalDemand;
  const activeVehicleIds = new Set((routes || []).map((r) => r.vehicle_id));

  return (
    <div className="panel" style={{ padding: '1.1rem' }}>

      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        paddingBottom: '0.75rem',
        borderBottom: '1px solid var(--beige-border)',
        marginBottom: '0.85rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Truck size={15} color="var(--green-mid)" />
          <h2 className="font-display" style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-ink)', margin: 0 }}>
            Fleet Inventory
          </h2>
        </div>
        <span className="badge-neutral">{vehicleCapacities.length} trucks</span>
      </div>

      {/* Capacity Alert */}
      <div style={{
        background: isCapacitySufficient ? 'var(--green-pale)' : 'var(--red-pale)',
        border: `1px solid ${isCapacitySufficient ? 'var(--green-light)' : '#D4A0A0'}`,
        borderRadius: 'var(--radius-xs)',
        padding: '0.6rem 0.75rem',
        display: 'flex', alignItems: 'flex-start', gap: '0.5rem',
        marginBottom: '0.85rem',
      }}>
        {isCapacitySufficient
          ? <CheckCircle2 size={13} color="var(--green-deep)" style={{ marginTop: 2, flexShrink: 0 }} />
          : <ShieldAlert size={13} color="var(--red-muted)" style={{ marginTop: 2, flexShrink: 0 }} />
        }
        <div>
          <p style={{ fontSize: '0.72rem', fontWeight: 700, color: isCapacitySufficient ? 'var(--green-deep)' : 'var(--red-muted)', margin: 0 }}>
            {isCapacitySufficient ? 'Fleet capacity sufficient' : 'Capacity alert — demand exceeds fleet!'}
          </p>
          <p className="font-mono-data" style={{ fontSize: '0.68rem', color: 'var(--text-muted)', margin: '0.2rem 0 0' }}>
            Fleet {(totalFleetCapacity / 1000).toFixed(0)}t &nbsp;|&nbsp; Demand {(totalDemand / 1000).toFixed(1)}t
          </p>
        </div>
      </div>

      {/* Vehicle List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '260px', overflowY: 'auto' }}>
        {vehicleCapacities.map((cap, idx) => {
          const vehicleId = idx + 1;
          const isDeployed = activeVehicleIds.has(vehicleId);
          const color = getVehicleColor(vehicleId);
          const assignedRoute = (routes || []).find((r) => r.vehicle_id === vehicleId);
          const loadKg = assignedRoute?.load_kg || 0;

          return (
            <div
              key={idx}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '0.5rem 0.7rem',
                background: isDeployed ? 'var(--bg-raised)' : 'var(--bg-base)',
                border: `1.5px solid ${isDeployed ? 'var(--beige-border)' : 'transparent'}`,
                borderRadius: 'var(--radius-xs)',
                opacity: isDeployed ? 1 : 0.55,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <span style={{
                  width: 24, height: 24, borderRadius: '50%',
                  background: isDeployed ? color : 'var(--beige-mid)',
                  color: '#fff',
                  fontSize: '0.65rem', fontWeight: 900,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexShrink: 0,
                }}>{vehicleId}</span>
                <div>
                  <p style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-ink)', margin: 0 }}>
                    Truck {vehicleId}
                  </p>
                  <p className="font-mono-data" style={{ fontSize: '0.62rem', color: 'var(--text-faint)', margin: 0 }}>
                    {(cap / 1000).toFixed(0)}t cap · {cap.toLocaleString()} kg
                  </p>
                </div>
              </div>

              {isDeployed ? (
                <span style={{
                  fontSize: '0.65rem', fontWeight: 700,
                  background: `${color}22`, color: color,
                  border: `1px solid ${color}55`,
                  borderRadius: 'var(--radius-xs)',
                  padding: '0.15rem 0.5rem',
                }}>
                  {(loadKg / 1000).toFixed(1)}t loaded
                </span>
              ) : (
                <span className="badge-neutral">standby</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
