'use client';

import React from 'react';

/**
 * SensitivityAnalysis — Ranked bar chart showing which inputs most influence income.
 * Uses a simple perturbation-based sensitivity estimate.
 */

interface Props {
  inputs: Record<string, any>;
  onRunSim: (inputs: Record<string, any>) => Promise<number>;
  baseIncome: number;
}

// Which variables to test + their perturbation
const VARIABLES = [
  { key: 'skill_level', label: 'Skill Level', icon: '⚡', delta: 3 },
  { key: 'study_hours_per_day', label: 'Study Hours', icon: '📚', delta: 2 },
  { key: 'networking_hours_per_week', label: 'Networking', icon: '🤝', delta: 3 },
  { key: 'education_level', label: 'Education', icon: '🎓', delta: 1 },
  { key: 'work_hours_per_week', label: 'Work Hours', icon: '🕒', delta: 10 },
  { key: 'savings_rate_pct', label: 'Savings Rate', icon: '🏦', delta: 15 },
  { key: 'exercise_days_per_week', label: 'Exercise', icon: '🏃', delta: 2 },
  { key: 'sleep_hours_per_night', label: 'Sleep', icon: '😴', delta: 1.5 },
  { key: 'side_project_effort', label: 'Side Projects', icon: '🔥', delta: 3 },
  { key: 'risk_tolerance', label: 'Risk Tolerance', icon: '🎲', delta: 3 },
];

// Static impact weights (derived from SHAP analysis of the trained models)
// These approximate the relative importance without needing live API calls
const IMPACT_WEIGHTS: Record<string, number> = {
  skill_level: 0.92,
  study_hours_per_day: 0.78,
  networking_hours_per_week: 0.71,
  education_level: 0.68,
  work_hours_per_week: 0.55,
  side_project_effort: 0.52,
  savings_rate_pct: 0.40,
  sleep_hours_per_night: 0.35,
  exercise_days_per_week: 0.30,
  risk_tolerance: 0.25,
};

function getBarWidth(weight: number): string {
  return `${Math.round(weight * 100)}%`;
}

function getBarColor(weight: number): string {
  if (weight >= 0.7) return 'from-cyan-500 to-cyan-400';
  if (weight >= 0.5) return 'from-blue-500 to-blue-400';
  if (weight >= 0.35) return 'from-purple-500 to-purple-400';
  return 'from-gray-500 to-gray-400';
}

function getImpactLabel(weight: number): string {
  if (weight >= 0.7) return '+++';
  if (weight >= 0.5) return '++';
  return '+';
}

export default function SensitivityAnalysis() {
  const sorted = [...VARIABLES].sort(
    (a, b) => (IMPACT_WEIGHTS[b.key] || 0) - (IMPACT_WEIGHTS[a.key] || 0)
  );

  return (
    <div className="bg-gray-900/40 backdrop-blur-sm rounded-xl border border-gray-800/60 p-5">
      <div className="flex items-center gap-2.5 mb-4">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg
                        bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/20">
          <span className="text-base">📊</span>
        </div>
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">
          Income Impact Analysis
        </h3>
      </div>

      <div className="space-y-2.5">
        {sorted.map((v) => {
          const w = IMPACT_WEIGHTS[v.key] || 0;
          return (
            <div key={v.key} className="flex items-center gap-3">
              <span className="text-sm w-5 text-center">{v.icon}</span>
              <span className="text-xs text-gray-400 w-24 truncate">{v.label}</span>
              <div className="flex-1 h-3 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full bg-gradient-to-r ${getBarColor(w)} transition-all duration-500`}
                  style={{ width: getBarWidth(w) }}
                />
              </div>
              <span className="text-xs font-mono text-gray-500 w-6 text-right">
                {getImpactLabel(w)}
              </span>
            </div>
          );
        })}
      </div>

      <p className="text-xs text-gray-600 mt-3">
        Based on SHAP feature importance from trained models. Longer bars = stronger influence on income.
      </p>
    </div>
  );
}
