// frontend/src/components/Header.jsx
import React from 'react';
import { Truck, Sprout, Activity, ShieldCheck, AlertCircle } from 'lucide-react';

export default function Header({ backendConnected }) {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex items-center justify-between">
        
        {/* Brand & Logo */}
        <div className="flex items-center space-x-3">
          <div className="bg-emerald-600 text-white p-2 rounded-lg shadow-sm flex items-center justify-center">
            <Sprout className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">AgriRoute AI</h1>
              <span className="bg-emerald-100 text-emerald-800 text-xs font-semibold px-2 py-0.5 rounded-full border border-emerald-200">
                CVRP Optimizer
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Demand Forecasting & Multi-Vehicle Delivery Optimization
            </p>
          </div>
        </div>

        {/* Backend Status Badge */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs font-medium px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200">
            {backendConnected ? (
              <>
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </span>
                <span className="text-emerald-700 font-semibold">FastAPI Connected</span>
              </>
            ) : (
              <>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span>
                <span className="text-amber-700 font-medium">Connecting...</span>
              </>
            )}
          </div>
        </div>

      </div>
    </header>
  );
}
