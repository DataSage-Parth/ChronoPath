'use client';

import React from 'react';

/**
 * LifeTimeline — Translates income predictions into narrative milestones.
 * Shows when the user will cross key salary thresholds.
 */

type Currency = 'USD' | 'INR';

const CURRENCY_RATES = { USD: 1, INR: 83 } as const;

function fmt(amount: number, c: Currency): string {
  const v = amount * CURRENCY_RATES[c];
  const sym = c === 'INR' ? '₹' : '$';
  const loc = c === 'INR' ? 'en-IN' : 'en-US';
  return sym + v.toLocaleString(loc, { maximumFractionDigits: 0 });
}

interface SimData {
  years: number[];
  income: { percentiles: Record<number, number[]> };
  happiness: { percentiles: Record<number, number[]> };
  stress: { percentiles: Record<number, number[]> };
}

interface Props {
  data: SimData | null;
  age: number;
  currency: Currency;
}

interface Milestone {
  age: number;
  year: number;
  icon: string;
  text: string;
  color: string;
}

export default function LifeTimeline({ data, age, currency }: Props) {
  if (!data) return null;

  const median = data.income.percentiles[50] || [];
  const happiness = data.happiness.percentiles[50] || [];
  const stress = data.stress.percentiles[50] || [];
  const milestones: Milestone[] = [];

  // Income thresholds to check (in USD)
  const thresholds = [50000, 80000, 100000, 120000, 150000, 200000, 300000];
  const currentIncome = median[0] || 0;
  for (const t of thresholds) {
    if (currentIncome >= t) continue; // already past this
    const idx = median.findIndex(v => v >= t);
    if (idx >= 0) {
      milestones.push({
        age: age + idx + 1, year: idx + 1, icon: '💰',
        text: `Income crosses ${fmt(t, currency)}`,
        color: 'text-cyan-400',
      });
    }
  }

  // Happiness milestone
  const happyIdx = happiness.findIndex(v => v >= 7.5);
  if (happyIdx >= 0) {
    milestones.push({
      age: age + happyIdx + 1, year: happyIdx + 1, icon: '😊',
      text: 'High life satisfaction (7.5+/10)',
      color: 'text-emerald-400',
    });
  }

  // Stress warning
  const stressIdx = stress.findIndex(v => v >= 0.6);
  if (stressIdx >= 0) {
    milestones.push({
      age: age + stressIdx + 1, year: stressIdx + 1, icon: '⚠️',
      text: 'Stress risk becomes elevated (60%+)',
      color: 'text-amber-400',
    });
  }

  // Financial stability
  const stabilityIdx = median.findIndex((v, i) => v > currentIncome * 1.5 && (stress[i] || 0) < 0.4);
  if (stabilityIdx >= 0) {
    milestones.push({
      age: age + stabilityIdx + 1, year: stabilityIdx + 1, icon: '🛡️',
      text: 'Strong financial stability zone',
      color: 'text-purple-400',
    });
  }

  // Wealth acceleration
  const accelIdx = median.findIndex(v => v > currentIncome * 2);
  if (accelIdx >= 0) {
    milestones.push({
      age: age + accelIdx + 1, year: accelIdx + 1, icon: '🚀',
      text: 'Wealth accumulation accelerates (2× income)',
      color: 'text-cyan-300',
    });
  }

  // Sort by year, take top 5
  milestones.sort((a, b) => a.year - b.year);
  const display = milestones.slice(0, 5);

  if (display.length === 0) return null;

  return (
    <div className="bg-gray-900/40 backdrop-blur-sm rounded-xl border border-gray-800/60 p-5">
      <div className="flex items-center gap-2.5 mb-4">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg
                        bg-gradient-to-br from-purple-500/20 to-indigo-500/20 border border-purple-500/20">
          <span className="text-base">🗓️</span>
        </div>
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">
          Life Event Timeline
        </h3>
      </div>

      <div className="relative ml-4">
        {/* Vertical line */}
        <div className="absolute left-0 top-2 bottom-2 w-px bg-gray-700" />

        <div className="space-y-4">
          {display.map((m, i) => (
            <div key={i} className="flex items-start gap-3 relative pl-5">
              {/* Dot on timeline */}
              <div className="absolute left-[-4px] top-1.5 w-2 h-2 rounded-full bg-gray-500 ring-2 ring-gray-900" />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-gray-400">Age {m.age}</span>
                  <span className="text-xs text-gray-600">·</span>
                  <span className="text-xs text-gray-600">Year {m.year}</span>
                </div>
                <p className={`text-sm ${m.color} mt-0.5`}>
                  {m.icon} {m.text}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
