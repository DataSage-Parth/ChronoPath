'use client';

import React, { useState } from 'react';

/**
 * ModelTransparency — Collapsible "How ChronoPath Works" panel
 * explaining the simulation methodology in plain English.
 */

export default function ModelTransparency() {
  const [open, setOpen] = useState(false);

  return (
    <div className="bg-gray-900/40 backdrop-blur-sm rounded-xl border border-gray-800/60">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2.5 p-5 text-left hover:bg-gray-800/30 transition-colors rounded-xl"
      >
        <div className="flex items-center justify-center w-8 h-8 rounded-lg
                        bg-gradient-to-br from-gray-500/20 to-slate-500/20 border border-gray-500/20">
          <span className="text-base">🧠</span>
        </div>
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider flex-1">
          How ChronoPath Works
        </h3>
        <span className="text-gray-500 text-xs">{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className="px-5 pb-5 space-y-4 max-w-2xl">
          <div>
            <h4 className="text-xs font-semibold text-cyan-400 uppercase mb-1">Monte Carlo Simulation</h4>
            <p className="text-sm text-gray-400 leading-relaxed">
              ChronoPath runs <strong className="text-gray-300">10,000 simulations</strong> of your future, each with slightly
              different random factors (like market conditions, lucky breaks, or setbacks). The shaded bands
              on the chart show the range of outcomes — wider bands mean more uncertainty.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-purple-400 uppercase mb-1">Behavioral Modeling</h4>
            <p className="text-sm text-gray-400 leading-relaxed">
              Your decisions (study hours, networking, exercise, etc.) are combined using formulas based on
              research data. For example, study hours follow a <em>diminishing returns</em> curve — the first
              2 hours matter more than hours 5 and 6. These relationships make predictions more realistic.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-emerald-400 uppercase mb-1">Probability Ranges</h4>
            <p className="text-sm text-gray-400 leading-relaxed">
              Rather than one prediction, ChronoPath shows you the <strong className="text-gray-300">5th to 95th percentile</strong> range.
              The darker band covers the most likely 50% of outcomes. This honest approach shows that
              the future isn&apos;t a single line — it&apos;s a range of possibilities.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-amber-400 uppercase mb-1">Data Sources</h4>
            <p className="text-sm text-gray-400 leading-relaxed">
              Predictions are based on patterns from aggregated survey data (Stack Overflow Developer Survey,
              World Happiness Report, OECD statistics). No individual data is stored or used.
              All predictions are hypothetical scenarios, not guarantees.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
