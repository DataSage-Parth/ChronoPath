'use client';

import React, { useState } from 'react';

/**
 * GoalMode — Users set a target income + age, and ChronoPath generates
 * strategy recommendations for what to change.
 */

type Currency = 'USD' | 'INR';
const RATES = { USD: 1, INR: 83 } as const;

function fmt(amount: number, c: Currency): string {
  const v = amount * RATES[c];
  const sym = c === 'INR' ? '₹' : '$';
  return sym + v.toLocaleString(c === 'INR' ? 'en-IN' : 'en-US', { maximumFractionDigits: 0 });
}

interface Props {
  inputs: Record<string, any>;
  medianIncome10: number;
  currency: Currency;
}

interface Recommendation {
  icon: string;
  action: string;
  detail: string;
  impact: 'high' | 'medium' | 'low';
}

function generateRecommendations(
  inputs: Record<string, any>,
  targetIncome: number,
  currentIncome: number,
): Recommendation[] {
  const recs: Recommendation[] = [];
  const gap = targetIncome - currentIncome;
  if (gap <= 0) return [{ icon: '🎉', action: "You're already on track!", detail: 'Your current trajectory meets your goal.', impact: 'high' }];

  // Skill level
  if (inputs.skill_level < 8) {
    recs.push({
      icon: '⚡', impact: 'high',
      action: `Increase Skill Level to ${Math.min(10, inputs.skill_level + 2)}`,
      detail: 'Skill level has the highest impact on income. Invest in certifications and deep expertise.',
    });
  }

  // Study hours
  if (inputs.study_hours_per_day < 3) {
    recs.push({
      icon: '📚', impact: 'high',
      action: `Study ${Math.min(5, inputs.study_hours_per_day + 2)} hours/day`,
      detail: 'More learning time accelerates skill growth and long-term career trajectory.',
    });
  }

  // Networking
  if (inputs.networking_hours_per_week < 6) {
    recs.push({
      icon: '🤝', impact: 'medium',
      action: `Network ${Math.min(8, inputs.networking_hours_per_week + 3)} hours/week`,
      detail: 'Professional networking opens promotion and opportunity pathways.',
    });
  }

  // Industry change
  if (!['technology', 'finance'].includes(inputs.job_category)) {
    recs.push({
      icon: '🏢', impact: 'high',
      action: 'Consider switching to Technology or Finance',
      detail: 'These industries have the highest salary ceilings and growth rates.',
    });
  }

  // Side projects
  if (inputs.side_project_effort < 5) {
    recs.push({
      icon: '🔥', impact: 'medium',
      action: `Increase side project effort to ${Math.min(8, inputs.side_project_effort + 3)}`,
      detail: 'Side projects create additional income streams and accelerate learning.',
    });
  }

  // Education
  if (inputs.education_level < 3) {
    recs.push({
      icon: '🎓', impact: 'medium',
      action: 'Pursue a higher degree or professional certification',
      detail: 'Advanced education increases salary baseline and career ceiling.',
    });
  }

  // Savings
  if (inputs.savings_rate_pct < 25) {
    recs.push({
      icon: '🏦', impact: 'low',
      action: `Increase savings rate to ${Math.min(40, inputs.savings_rate_pct + 10)}%`,
      detail: 'Higher savings provide financial security for career risks.',
    });
  }

  return recs.slice(0, 5);
}

const IMPACT_COLORS = {
  high: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
  medium: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
  low: 'text-gray-400 bg-gray-500/10 border-gray-500/20',
};

export default function GoalMode({ inputs, medianIncome10, currency }: Props) {
  const [targetIncome, setTargetIncome] = useState(200000);
  const [targetAge, setTargetAge] = useState(35);
  const [showRecs, setShowRecs] = useState(false);

  const recs = generateRecommendations(inputs, targetIncome, medianIncome10);

  return (
    <div className="bg-gray-900/40 backdrop-blur-sm rounded-xl border border-gray-800/60 p-5">
      <div className="flex items-center gap-2.5 mb-4">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg
                        bg-gradient-to-br from-emerald-500/20 to-teal-500/20 border border-emerald-500/20">
          <span className="text-base">🎯</span>
        </div>
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">
          Goal Mode
        </h3>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label className="text-xs text-gray-500 block mb-1">Target Income ({currency})</label>
          <input
            type="number"
            value={targetIncome}
            onChange={(e) => setTargetIncome(Number(e.target.value))}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2
                       text-sm text-gray-200 focus:ring-2 focus:ring-emerald-500/50 focus:outline-none"
          />
          <p className="text-xs text-gray-600 mt-0.5">{fmt(targetIncome, currency)}</p>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Target Age</label>
          <input
            type="number"
            value={targetAge}
            min={inputs.age + 1}
            max={65}
            onChange={(e) => setTargetAge(Number(e.target.value))}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2
                       text-sm text-gray-200 focus:ring-2 focus:ring-emerald-500/50 focus:outline-none"
          />
        </div>
      </div>

      <button
        onClick={() => setShowRecs(true)}
        className="w-full py-2 rounded-lg text-xs font-semibold
                   bg-gradient-to-r from-emerald-600/80 to-teal-600/80
                   hover:from-emerald-500 hover:to-teal-500
                   transition-all duration-200 mb-3"
      >
        🎯 Generate Strategy
      </button>

      {showRecs && (
        <div>
          <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Goal Strategy
          </h4>
          <div className="space-y-2">
            {recs.map((r, i) => (
              <div key={i} className={`rounded-lg border p-3 ${IMPACT_COLORS[r.impact]}`}>
                <div className="flex items-center gap-2 mb-1">
                  <span>{r.icon}</span>
                  <span className="text-sm font-medium">{r.action}</span>
                  <span className="ml-auto text-[10px] uppercase opacity-60">{r.impact}</span>
                </div>
                <p className="text-xs opacity-70">{r.detail}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
