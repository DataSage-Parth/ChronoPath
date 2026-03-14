'use client';

import React from 'react';

/**
 * AIInsight — Generates a human-readable explanation of the simulation results
 * based on user inputs and outcome data.
 *
 * Placement: below Income Trajectory graph, above metric cards.
 *
 * Rules:
 *  - 3-5 sentences, simple English, no statistical jargon
 *  - Dynamic behavioral insights based on input thresholds
 *  - Currency-aware income formatting
 */

type Currency = 'USD' | 'INR';

const CURRENCY_CONFIG = {
  USD: { symbol: '$', rate: 1, locale: 'en-US' },
  INR: { symbol: '₹', rate: 83, locale: 'en-IN' },
} as const;

function formatCurrency(amount: number, currency: Currency): string {
  const cfg = CURRENCY_CONFIG[currency];
  const converted = amount * cfg.rate;
  if (currency === 'INR') {
    return cfg.symbol + converted.toLocaleString('en-IN', { maximumFractionDigits: 0 });
  }
  return cfg.symbol + converted.toLocaleString('en-US', { maximumFractionDigits: 0 });
}

// ── Education label lookup ──
const EDUCATION_LABELS: Record<number, string> = {
  0: 'High School', 1: 'Diploma', 2: "Bachelor's", 3: "Master's", 4: 'PhD', 5: 'Elite/MBA',
};

interface SimulationData {
  years: number[];
  income: { percentiles: Record<number, number[]>; sample_trajectories: number[][] };
  happiness: { percentiles: Record<number, number[]>; sample_trajectories: number[][] };
  stress: { percentiles: Record<number, number[]>; sample_trajectories: number[][] };
}

interface UserInputs {
  age: number;
  education_level: number;
  years_experience: number;
  study_hours_per_day: number;
  work_hours_per_week: number;
  savings_rate_pct: number;
  exercise_days_per_week: number;
  networking_hours_per_week: number;
  sleep_hours_per_night: number;
  social_media_hours_per_day: number;
  skill_level: number;
  risk_tolerance: number;
  side_project_effort: number;
  job_category: string;
  country: string;
}

interface AIInsightProps {
  data: SimulationData | null;
  inputs: UserInputs;
  currency: Currency;
}

function generateInsight(data: SimulationData, inputs: UserInputs, currency: Currency): string[] {
  const medianIncome10 = data.income.percentiles[50]?.[9] ?? 0;
  const medianIncome20 = data.income.percentiles[50]?.[19] ?? medianIncome10;
  const low10 = data.income.percentiles[5]?.[9] ?? 0;
  const high10 = data.income.percentiles[95]?.[9] ?? 0;
  const happiness10 = data.happiness.percentiles[50]?.[9] ?? 0;
  const stress10 = (data.stress.percentiles[50]?.[9] ?? 0) * 100;

  const sentences: string[] = [];

  // ── Base explanation: what the graph means ──
  const incomeFormatted = formatCurrency(medianIncome10, currency);
  const lowFormatted = formatCurrency(low10, currency);
  const highFormatted = formatCurrency(high10, currency);

  // Determine trajectory direction
  const incomeYear1 = data.income.percentiles[50]?.[0] ?? 0;
  let trajectory = 'remain relatively stable';
  if (medianIncome10 > incomeYear1 * 1.3) trajectory = 'grow significantly';
  else if (medianIncome10 > incomeYear1 * 1.1) trajectory = 'grow steadily';
  else if (medianIncome10 < incomeYear1 * 0.95) trajectory = 'face some headwinds';

  sentences.push(
    `Based on your current decisions, your income is expected to ${trajectory} over the next 20 years. ` +
    `The bright line shows your most likely income path, while the shaded bands represent the range of possible outcomes.`
  );

  sentences.push(
    `Your median income after 10 years is projected to reach approximately ${incomeFormatted}, ` +
    `with outcomes ranging from ${lowFormatted} to ${highFormatted} depending on market conditions and opportunities.`
  );

  // ── Behavioral insights (pick the most relevant 1-2) ──
  const insights: string[] = [];

  if (inputs.study_hours_per_day > 3) {
    insights.push(
      'Because you invest significant time in learning, your long-term career growth potential is higher than average.'
    );
  }

  if (inputs.networking_hours_per_week > 6) {
    insights.push(
      'Your active networking habit increases your chances of finding better opportunities and promotions.'
    );
  }

  if (inputs.work_hours_per_week > 55) {
    insights.push(
      'Your work hours are relatively high — this may boost income in the short term but could increase stress risk over time.'
    );
  }

  if (inputs.savings_rate_pct > 30) {
    insights.push(
      'A strong savings habit like yours builds financial security and gives you more freedom to take career risks.'
    );
  }

  if (inputs.exercise_days_per_week > 3) {
    insights.push(
      'Regular exercise helps reduce burnout and improves overall life satisfaction, supporting long-term productivity.'
    );
  }

  if (inputs.sleep_hours_per_night < 6) {
    insights.push(
      'Getting less than 6 hours of sleep can increase stress and reduce cognitive performance — consider prioritizing rest.'
    );
  }

  if (inputs.social_media_hours_per_day > 4) {
    insights.push(
      'Spending more than 4 hours daily on social media may gradually reduce happiness and focus — moderation could help.'
    );
  }

  if (inputs.side_project_effort > 6) {
    insights.push(
      'Your strong side-project effort creates additional income pathways and accelerates skill development.'
    );
  }

  if (inputs.skill_level >= 8) {
    insights.push(
      'With an expert-level skill set, you are well-positioned for senior roles and higher compensation.'
    );
  }

  // Add up to 2 behavioral insights
  sentences.push(...insights.slice(0, 2));

  // ── Closing with happiness/stress context ──
  if (stress10 > 60) {
    sentences.push(
      `Your current lifestyle puts your stress risk at around ${stress10.toFixed(0)}% — ` +
      `consider adjusting work hours, sleep, or exercise to bring this down.`
    );
  } else if (happiness10 >= 7) {
    sentences.push(
      `Your projected happiness score of ${happiness10.toFixed(1)}/10 suggests a well-balanced lifestyle. Keep it up!`
    );
  }

  return sentences;
}

export default function AIInsight({ data, inputs, currency }: AIInsightProps) {
  if (!data) return null;

  const sentences = generateInsight(data, inputs, currency);

  return (
    <div className="bg-gray-900/40 backdrop-blur-sm rounded-xl border border-gray-800/60 p-5
                    hover:border-cyan-900/30 transition-colors duration-300">
      {/* Header */}
      <div className="flex items-center gap-2.5 mb-3">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg
                        bg-gradient-to-br from-amber-500/20 to-orange-500/20
                        border border-amber-500/20">
          <span className="text-base">💡</span>
        </div>
        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">
          AI Insight
        </h3>
      </div>

      {/* Insight text */}
      <div className="space-y-2 max-w-2xl">
        {sentences.map((sentence, i) => (
          <p key={i} className="text-sm text-gray-400 leading-relaxed">
            {sentence}
          </p>
        ))}
      </div>
    </div>
  );
}
