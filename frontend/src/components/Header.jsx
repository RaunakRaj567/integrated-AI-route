// frontend/src/components/Header.jsx
import React from 'react';
import { Sprout } from 'lucide-react';

export default function Header({ backendConnected }) {
  return (
    <header style={{
      background: 'var(--bg-raised)',
      borderBottom: '1.5px solid var(--beige-border)',
      position: 'sticky',
      top: 0,
      zIndex: 30,
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '0.9rem 2rem',
        display: 'grid',
        gridTemplateColumns: '1fr auto 1fr',
        alignItems: 'center',
        gap: '1rem',
      }}>
        {/* Left — Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{
            width: 36, height: 36,
            background: 'var(--green-deep)',
            borderRadius: 'var(--radius-sm)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0,
          }}>
            <Sprout size={18} color="#FBF8F2" />
          </div>
          <div>
            <h1 className="font-display" style={{
              fontSize: '1.25rem',
              fontWeight: 700,
              color: 'var(--text-ink)',
              lineHeight: 1.1,
              margin: 0,
            }}>
              AgriRoute <em style={{ color: 'var(--green-mid)', fontStyle: 'italic' }}>AI</em>
            </h1>
            <p style={{ fontSize: '0.65rem', color: 'var(--text-faint)', margin: 0, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
              Demand Forecasting & Multi-Vehicle Logistics
            </p>
          </div>
        </div>

        {/* Center — Title strip */}
        <div style={{
          background: 'var(--green-pale)',
          border: '1px solid var(--green-light)',
          borderRadius: 'var(--radius-xs)',
          padding: '0.3rem 1rem',
          textAlign: 'center',
        }}>
          <span className="text-label-caps" style={{ color: 'var(--green-deep)' }}>
            Delhi-NCR Agricultural Optimization Portal
          </span>
        </div>

        {/* Right — Status */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '0.5rem' }}>
          <span className="text-label-caps" style={{ color: 'var(--text-faint)' }}>Backend</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{
              width: 8, height: 8, borderRadius: '50%',
              background: backendConnected ? 'var(--green-mid)' : '#D4A04A',
              display: 'inline-block',
              animation: backendConnected ? 'none' : undefined,
            }} />
            <span className="font-mono-data" style={{
              fontSize: '0.72rem',
              color: backendConnected ? 'var(--green-deep)' : 'var(--amber-warm)',
              fontWeight: 500,
            }}>
              {backendConnected ? 'Connected' : 'Connecting…'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
