'use client';

import React, { useState, useCallback, useMemo } from 'react';
import DecisionSlider from './DecisionSlider';
import IncomeCurve from './IncomeCurve';
import AIInsight from './AIInsight';
import LifeTimeline from './LifeTimeline';
import SensitivityAnalysis from './SensitivityAnalysis';
import GoalMode from './GoalMode';
import ModelTransparency from './ModelTransparency';
import CountryContext from './CountryContext';
import InfoTooltip from './InfoTooltip';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ─── Currency Config ───
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

// ─── Education Labels ───
const EDUCATION_OPTIONS = [
  { value: 0, label: 'High School' },
  { value: 1, label: 'Diploma' },
  { value: 2, label: "Bachelor's Degree" },
  { value: 3, label: "Master's Degree" },
  { value: 4, label: 'PhD' },
  { value: 5, label: 'Elite / MBA' },
];

// ─── Job Categories ───
const JOB_CATEGORIES = [
  { value: 'technology', label: '💻 Technology' },
  { value: 'finance', label: '💹 Finance' },
  { value: 'healthcare', label: '🏥 Healthcare' },
  { value: 'education', label: '📖 Education' },
  { value: 'government', label: '🏛️ Government' },
  { value: 'creative_media', label: '🎨 Creative / Media' },
  { value: 'entrepreneurship', label: '🚀 Entrepreneurship' },
];

// ─── Default Inputs ───
const DEFAULT_INPUTS = {
  age: 28, education_level: 3, years_experience: 5, country: 'USA',
  job_category: 'technology', skill_level: 6, study_hours_per_day: 2.0,
  networking_hours_per_week: 4.0, work_hours_per_week: 40.0,
  exercise_days_per_week: 3, sleep_hours_per_night: 7.0,
  social_media_hours_per_day: 2.0, savings_rate_pct: 20.0,
  risk_tolerance: 5, side_project_effort: 3,
};

// ─── Preset Scenarios ───
const PRESETS: Record<string, { label: string; icon: string; overrides: Partial<typeof DEFAULT_INPUTS> }> = {
  career: {
    label: 'Career Focus', icon: '🎯',
    overrides: { study_hours_per_day: 5, networking_hours_per_week: 7, work_hours_per_week: 50, skill_level: 8, side_project_effort: 6 },
  },
  health: {
    label: 'Health Focus', icon: '💚',
    overrides: { exercise_days_per_week: 5, sleep_hours_per_night: 8, work_hours_per_week: 38, social_media_hours_per_day: 1 },
  },
  wealth: {
    label: 'Aggressive Wealth', icon: '💎',
    overrides: { savings_rate_pct: 45, risk_tolerance: 8, side_project_effort: 8, work_hours_per_week: 55, study_hours_per_day: 3 },
  },
  balanced: {
    label: 'Balanced Life', icon: '⚖️',
    overrides: { work_hours_per_week: 40, exercise_days_per_week: 4, sleep_hours_per_night: 7.5, study_hours_per_day: 2, social_media_hours_per_day: 1.5, savings_rate_pct: 25 },
  },
};

interface SimulationData {
  years: number[];
  income: { percentiles: Record<number, number[]>; sample_trajectories: number[][] };
  happiness: { percentiles: Record<number, number[]>; sample_trajectories: number[][] };
  stress: { percentiles: Record<number, number[]>; sample_trajectories: number[][] };
}

// ─── Collapsible Section ───
function InputSection({ title, icon, children, defaultOpen = true }: {
  title: string; icon: string; children: React.ReactNode; defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="mb-3">
      <button onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-3 py-2 rounded-lg bg-gray-800/50 hover:bg-gray-800/80 transition-colors text-left">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">{icon} {title}</span>
        <span className="text-gray-500 text-xs">{open ? '▲' : '▼'}</span>
      </button>
      {open && <div className="mt-2 space-y-1 px-1">{children}</div>}
    </div>
  );
}

// ─── Styled Dropdown ───
function StyledDropdown({ id, label, icon, value, options, tooltip, onChange }: {
  id: string; label: string; icon: string; value: string | number;
  options: { value: string | number; label: string }[];
  tooltip?: string; onChange: (val: string) => void;
}) {
  return (
    <div className="mb-3" title={tooltip}>
      <label htmlFor={id} className="text-sm font-medium text-gray-300 block mb-1">{icon} {label}</label>
      <select id={id} value={value} onChange={(e) => onChange(e.target.value)}
        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:ring-2 focus:ring-cyan-500/50 focus:outline-none cursor-pointer transition-colors hover:border-gray-600">
        {options.map((opt) => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
      </select>
    </div>
  );
}

// ─── Scenario Tab ───
type ScenarioId = 'A' | 'B';

// ─── Main App ───
export default function SimulatorApp() {
  const [inputsA, setInputsA] = useState({ ...DEFAULT_INPUTS });
  const [inputsB, setInputsB] = useState({ ...DEFAULT_INPUTS, work_hours_per_week: 50, study_hours_per_day: 4, skill_level: 8 });
  const [activeScenario, setActiveScenario] = useState<ScenarioId>('A');
  const [simDataA, setSimDataA] = useState<SimulationData | null>(null);
  const [simDataB, setSimDataB] = useState<SimulationData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currency, setCurrency] = useState<Currency>('USD');
  const [compareMode, setCompareMode] = useState(false);

  const inputs = activeScenario === 'A' ? inputsA : inputsB;
  const setInputs = activeScenario === 'A' ? setInputsA : setInputsB;

  const updateInput = useCallback((key: string, value: number | string) => {
    setInputs((prev) => {
      const next = { ...prev, [key]: value };
      if (key === 'age') {
        const maxExp = (value as number) - 18;
        if (next.years_experience > maxExp) next.years_experience = Math.max(0, maxExp);
      }
      if (key === 'years_experience') {
        const maxExp = next.age - 18;
        if ((value as number) > maxExp) next.years_experience = maxExp;
      }
      return next;
    });
  }, [setInputs]);

  const applyPreset = useCallback((presetKey: string) => {
    const preset = PRESETS[presetKey];
    if (!preset) return;
    setInputs((prev) => ({ ...prev, ...preset.overrides }));
  }, [setInputs]);

  const runSimulation = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const simA = fetch(`${API_URL}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inputs: inputsA, n_simulations: 10000, years_horizon: 20, random_seed: 42 }),
      }).then(r => { if (!r.ok) throw new Error(`API error: ${r.status}`); return r.json(); });

      if (compareMode) {
        const simB = fetch(`${API_URL}/simulate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ inputs: inputsB, n_simulations: 10000, years_horizon: 20, random_seed: 42 }),
        }).then(r => { if (!r.ok) throw new Error(`API error: ${r.status}`); return r.json(); });

        const [dataA, dataB] = await Promise.all([simA, simB]);
        setSimDataA(dataA);
        setSimDataB(dataB);
      } else {
        const dataA = await simA;
        setSimDataA(dataA);
        setSimDataB(null);
      }
    } catch (e: any) {
      setError(e.message || 'Failed to run simulation');
    } finally {
      setLoading(false);
    }
  }, [inputsA, inputsB, compareMode]);

  const maxExperience = useMemo(() => Math.max(0, inputs.age - 18), [inputs.age]);
  const simData = activeScenario === 'A' ? simDataA : simDataB;
  const primaryData = simDataA; // main data for insight/timeline

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* ── HEADER ── */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-3">
          <span className="text-2xl">⏳</span>
          <div>
            <h1 className="text-lg font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent leading-tight">
              ChronoPath
            </h1>
            <p className="text-[10px] text-gray-500 leading-tight">Explore how your decisions shape your future.</p>
          </div>
          <div className="ml-auto flex items-center gap-3">
            {/* Compare toggle */}
            <button
              onClick={() => setCompareMode(!compareMode)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all border
                ${compareMode
                  ? 'bg-purple-500/20 border-purple-500/40 text-purple-300'
                  : 'bg-gray-800 border-gray-700 text-gray-500 hover:border-gray-600'}`}
            >
              {compareMode ? '⚡ Compare ON' : '🔀 Compare'}
            </button>
            <select value={currency} onChange={(e) => setCurrency(e.target.value as Currency)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-2 py-1 text-xs text-gray-300 focus:ring-2 focus:ring-cyan-500/50 focus:outline-none cursor-pointer"
              aria-label="Currency">
              <option value="USD">$ USD</option>
              <option value="INR">₹ INR</option>
            </select>
            <span className="text-xs text-gray-600">v1.0</span>
          </div>
        </div>
      </header>

      {/* ── MAIN LAYOUT ── */}
      <div className="max-w-7xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ── INPUT PANEL ── */}
        <aside className="lg:col-span-1 space-y-2">
          <div className="bg-gray-900/60 backdrop-blur rounded-2xl border border-gray-800 p-4">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
              🎛️ Your Life Decisions
            </h2>

            {/* Scenario Tabs (when compare mode is on) */}
            {compareMode && (
              <div className="flex gap-2 mb-3">
                {(['A', 'B'] as ScenarioId[]).map((s) => (
                  <button key={s} onClick={() => setActiveScenario(s)}
                    className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all border
                      ${activeScenario === s
                        ? s === 'A'
                          ? 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300'
                          : 'bg-purple-500/20 border-purple-500/40 text-purple-300'
                        : 'bg-gray-800 border-gray-700 text-gray-500 hover:border-gray-600'}`}>
                    {s === 'A' ? '🔵' : '🟣'} Scenario {s}
                  </button>
                ))}
              </div>
            )}

            {/* Quick Presets */}
            <div className="mb-3">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1.5">Quick Presets</p>
              <div className="grid grid-cols-2 gap-1.5">
                {Object.entries(PRESETS).map(([key, p]) => (
                  <button key={key} onClick={() => applyPreset(key)}
                    className="px-2 py-1.5 rounded-lg text-[11px] font-medium bg-gray-800/60 border border-gray-700/50 text-gray-400 hover:border-gray-600 hover:text-gray-300 transition-all active:scale-[0.97]">
                    {p.icon} {p.label}
                  </button>
                ))}
              </div>
            </div>

            {/* GROUP 1: Personal Information */}
            <InputSection title="Personal Information" icon="👤" defaultOpen={true}>
              <DecisionSlider id="age" label="🎂 Age" min={18} max={65} step={1}
                value={inputs.age} unit=" yrs"
                tooltip="Your current age. Determines maximum years of experience."
                onChange={(v) => updateInput('age', v)} />
              <StyledDropdown id="country" label="Country / Region" icon="🌍"
                value={inputs.country}
                tooltip="Your country. Affects salary baseline due to regional cost of living."
                options={[
                  { value: 'USA', label: '🇺🇸 United States' }, { value: 'GBR', label: '🇬🇧 United Kingdom' },
                  { value: 'DEU', label: '🇩🇪 Germany' }, { value: 'CAN', label: '🇨🇦 Canada' },
                  { value: 'AUS', label: '🇦🇺 Australia' }, { value: 'IND', label: '🇮🇳 India' },
                  { value: 'BRA', label: '🇧🇷 Brazil' },
                ]}
                onChange={(v) => updateInput('country', v)} />
              <StyledDropdown id="education" label="Education Level" icon="🎓"
                value={inputs.education_level}
                tooltip="Higher education increases salary baseline and career ceiling."
                options={EDUCATION_OPTIONS.map(e => ({ value: e.value.toString(), label: e.label }))}
                onChange={(v) => updateInput('education_level', parseInt(v))} />
              <DecisionSlider id="experience" label="💼 Years Experience" min={0} max={maxExperience} step={1}
                value={inputs.years_experience} unit=" yrs"
                tooltip={`Professional experience (max ${maxExperience} based on age).`}
                onChange={(v) => updateInput('years_experience', v)} />
            </InputSection>

            {/* GROUP 2: Career Development */}
            <InputSection title="Career Development" icon="📈" defaultOpen={true}>
              <StyledDropdown id="job-cat" label="Industry" icon="🏢"
                value={inputs.job_category}
                tooltip="Your industry sector. Affects income potential, stress, and growth."
                options={JOB_CATEGORIES}
                onChange={(v) => updateInput('job_category', v)} />
              <div className="relative">
                <DecisionSlider id="skill" label="⚡ Skill Level" min={0} max={10} step={1}
                  value={inputs.skill_level}
                  tooltip="Professional skill level (0=beginner, 10=world-class)."
                  onChange={(v) => updateInput('skill_level', v)}
                  infoTooltip={
                    <InfoTooltip
                      title="Skill Level"
                      description="Represents your professional expertise in your field. Higher skill levels increase promotion probability and long-term income growth."
                      scale={['0–2 → Beginner', '3–4 → Basic', '5–6 → Intermediate', '7–8 → Advanced', '9–10 → Expert']}
                    />
                  }
                />
              </div>
              <div className="relative">
                <DecisionSlider id="study" label="📚 Study Hours/Day" min={0} max={6} step={0.5}
                  value={inputs.study_hours_per_day} unit=" hrs"
                  tooltip="Time spent improving professional skills."
                  onChange={(v) => updateInput('study_hours_per_day', v)}
                  infoTooltip={
                    <InfoTooltip
                      title="Study Hours"
                      description="Daily time spent learning or improving professional skills. Consistent study increases skill growth and future income potential."
                      scale={['0 → None', '1–2 → Light learning', '3–4 → Skill development', '5–6 → Intensive learning']}
                    />
                  }
                />
              </div>
              <div className="relative">
                <DecisionSlider id="networking" label="🤝 Networking Hrs/Week" min={0} max={10} step={0.5}
                  value={inputs.networking_hours_per_week} unit=" hrs"
                  tooltip="Time building professional relationships."
                  onChange={(v) => updateInput('networking_hours_per_week', v)}
                  infoTooltip={
                    <InfoTooltip
                      title="Networking Hours"
                      description="Time spent building professional relationships through events, communities, or online platforms. Networking improves career opportunities and promotion likelihood."
                      scale={['0 → None', '1–2 → Occasional', '3–5 → Active', '6–8 → Strong networker', '9–10 → Industry connector']}
                    />
                  }
                />
              </div>
            </InputSection>

            {/* GROUP 3: Work Lifestyle */}
            <InputSection title="Work Lifestyle" icon="⚖️" defaultOpen={true}>
              <DecisionSlider id="work" label="🕒 Work Hours/Week" min={20} max={70} step={1}
                value={inputs.work_hours_per_week} unit=" hrs"
                tooltip="Weekly work hours. Above 40 hrs increases stress."
                onChange={(v) => updateInput('work_hours_per_week', v)} />
              <DecisionSlider id="exercise" label="🏃 Exercise Days/Week" min={0} max={7} step={1}
                value={inputs.exercise_days_per_week} unit=" days"
                tooltip="Regular exercise reduces stress and boosts happiness."
                onChange={(v) => updateInput('exercise_days_per_week', v)} />
              <DecisionSlider id="sleep" label="😴 Sleep Hours/Night" min={4} max={10} step={0.5}
                value={inputs.sleep_hours_per_night} unit=" hrs"
                tooltip="Optimal: 7-8 hours. Below 6 increases stress."
                onChange={(v) => updateInput('sleep_hours_per_night', v)} />
              <DecisionSlider id="social-media" label="📱 Social Media Hrs/Day" min={0} max={8} step={0.5}
                value={inputs.social_media_hours_per_day} unit=" hrs"
                tooltip="Above 2 hrs reduces happiness. Moderate use is neutral."
                onChange={(v) => updateInput('social_media_hours_per_day', v)} />
            </InputSection>

            {/* GROUP 4: Financial Behavior */}
            <InputSection title="Financial Behavior" icon="💰" defaultOpen={true}>
              <DecisionSlider id="savings" label="🏦 Savings Rate" min={0} max={60} step={1}
                value={inputs.savings_rate_pct} unit="%"
                tooltip="Percentage of income saved."
                onChange={(v) => updateInput('savings_rate_pct', v)} />
              <div className="relative">
                <DecisionSlider id="risk" label="🎲 Risk Tolerance" min={0} max={10} step={1}
                  value={inputs.risk_tolerance}
                  tooltip="0=conservative, 10=aggressive."
                  onChange={(v) => updateInput('risk_tolerance', v)}
                  infoTooltip={
                    <InfoTooltip
                      title="Risk Tolerance"
                      description="Your willingness to take financial or career risks. Higher risk tolerance may lead to higher potential rewards but greater uncertainty."
                      scale={['0–2 → Very conservative', '3–4 → Conservative', '5–6 → Balanced', '7–8 → Growth oriented', '9–10 → High risk']}
                    />
                  }
                />
              </div>
              <div className="relative">
                <DecisionSlider id="side-project" label="🔥 Side Project Effort" min={0} max={10} step={1}
                  value={inputs.side_project_effort}
                  tooltip="Boosts income growth and learning."
                  onChange={(v) => updateInput('side_project_effort', v)}
                  infoTooltip={
                    <InfoTooltip
                      title="Side Project Effort"
                      description="Time spent building projects, freelancing, or experimenting outside your main job. Side projects can accelerate skill growth and create new opportunities."
                      scale={['0 → None', '1–2 → Occasional', '3–4 → Consistent', '5–6 → Active builder', '7–8 → Serious builder', '9–10 → Startup-level effort']}
                    />
                  }
                />
              </div>
            </InputSection>

            {/* Run Button */}
            <button onClick={runSimulation} disabled={loading}
              className="w-full mt-3 py-3 rounded-xl font-semibold text-sm bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-cyan-500/20 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 active:scale-[0.98]">
              {loading
                ? '⏳ Simulating...'
                : compareMode
                  ? '🚀 Run Both Scenarios'
                  : '🚀 Run Simulation'}
            </button>
          </div>

          {/* Goal Mode — in sidebar */}
          {primaryData && (
            <GoalMode
              inputs={inputsA}
              medianIncome10={primaryData.income.percentiles[50]?.[9] || 0}
              currency={currency}
            />
          )}

          <p className="text-xs text-gray-600 px-2">
            ⚠️ Predictions are hypothetical scenarios, not guarantees.
          </p>
        </aside>

        {/* ── RESULTS PANEL ── */}
        <main className="lg:col-span-2 space-y-4">
          {error && (
            <div className="bg-red-900/30 border border-red-800 rounded-xl p-4 text-red-300 text-sm">
              ❌ {error}
            </div>
          )}

          {/* Income Chart (with optional comparison overlay) */}
          <IncomeCurve data={simDataA} dataB={compareMode ? simDataB : null} loading={loading} currency={currency} />

          {/* AI Insight */}
          <AIInsight data={primaryData} inputs={inputsA} currency={currency} />

          {/* Life Event Timeline */}
          <LifeTimeline data={primaryData} age={inputsA.age} currency={currency} />

          {/* Metric Cards */}
          {primaryData && (
            <div className={`grid grid-cols-1 ${compareMode && simDataB ? 'sm:grid-cols-2' : 'sm:grid-cols-3'} gap-4`}>
              {/* INCOME */}
              <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4 text-center hover:border-cyan-800/50 transition-colors">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">💰 Median Income (Yr 10)</p>
                {compareMode && simDataB ? (
                  <div className="flex items-center justify-center gap-3">
                    <div>
                      <p className="text-[10px] text-cyan-500">Scenario A</p>
                      <p className="text-xl font-bold text-cyan-400">
                        {formatCurrency(simDataA!.income.percentiles[50]?.[9] || 0, currency)}
                      </p>
                    </div>
                    <span className="text-gray-600">vs</span>
                    <div>
                      <p className="text-[10px] text-purple-500">Scenario B</p>
                      <p className="text-xl font-bold text-purple-400">
                        {formatCurrency(simDataB.income.percentiles[50]?.[9] || 0, currency)}
                      </p>
                    </div>
                  </div>
                ) : (
                  <p className="text-2xl font-bold text-cyan-400">
                    {formatCurrency(primaryData.income.percentiles[50]?.[9] || 0, currency)}
                  </p>
                )}
              </div>

              {/* HAPPINESS */}
              <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4 text-center hover:border-emerald-800/50 transition-colors">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">😊 Happiness (Yr 10)</p>
                {compareMode && simDataB ? (
                  <div className="flex items-center justify-center gap-3">
                    <div>
                      <p className="text-[10px] text-cyan-500">A</p>
                      <p className="text-xl font-bold text-emerald-400">
                        {(simDataA!.happiness.percentiles[50]?.[9] || 0).toFixed(1)}
                      </p>
                    </div>
                    <span className="text-gray-600">vs</span>
                    <div>
                      <p className="text-[10px] text-purple-500">B</p>
                      <p className="text-xl font-bold text-purple-300">
                        {(simDataB.happiness.percentiles[50]?.[9] || 0).toFixed(1)}
                      </p>
                    </div>
                  </div>
                ) : (
                  <p className="text-2xl font-bold text-emerald-400">
                    {(primaryData.happiness.percentiles[50]?.[9] || 0).toFixed(1)}/10
                  </p>
                )}
              </div>

              {/* STRESS */}
              {(!compareMode || !simDataB) && (
                <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4 text-center hover:border-rose-800/50 transition-colors">
                  <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">😰 Stress Risk (Yr 10)</p>
                  <p className="text-2xl font-bold text-rose-400">
                    {((primaryData.stress.percentiles[50]?.[9] || 0) * 100).toFixed(0)}%
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Bottom row: Sensitivity + Country Context side by side */}
          {primaryData && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <SensitivityAnalysis />
              <CountryContext country={inputsA.country} currency={currency} />
            </div>
          )}

          {/* Model Transparency */}
          <ModelTransparency />
        </main>
      </div>
    </div>
  );
}
