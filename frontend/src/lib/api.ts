/**
 * API client for the ChronoPath backend.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface UserInputs {
  // Group 1: Personal Information
  age: number;
  education_level: number;
  years_experience: number;
  country: string;

  // Group 2: Career Development
  job_category: string;
  skill_level: number;
  study_hours_per_day: number;
  networking_hours_per_week: number;

  // Group 3: Work Lifestyle
  work_hours_per_week: number;
  exercise_days_per_week: number;
  sleep_hours_per_night: number;
  social_media_hours_per_day: number;

  // Group 4: Financial Behavior
  savings_rate_pct: number;
  risk_tolerance: number;
  side_project_effort: number;
}

export interface PercentileData {
  percentiles: Record<number, number[]>;
  sample_trajectories: number[][];
}

export interface SimulationResponse {
  years: number[];
  income: PercentileData;
  happiness: PercentileData;
  stress: PercentileData;
  config: Record<string, unknown>;
}

export interface TrajectoryResponse {
  predicted_income: number;
  predicted_happiness: number;
  predicted_stress_probability: number;
  confidence_intervals: Record<string, { lower_95: number; upper_95: number }>;
  feature_importances: Record<string, number>;
}

export interface ExplainResponse {
  base_value: number;
  prediction: number;
  contributions: Array<{
    feature: string;
    value: number;
    shap_value: number;
    direction: 'positive' | 'negative';
  }>;
}

export interface AdviceResponse {
  answer: string;
  action_items: Array<{ action: string; change?: string; impact: string }>;
  top_factors: string[];
}

async function apiFetch<T>(endpoint: string, body: unknown): Promise<T> {
  const resp = await fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(err.detail || `API error: ${resp.status}`);
  }
  return resp.json();
}

export const api = {
  predictTrajectory: (inputs: UserInputs) =>
    apiFetch<TrajectoryResponse>('/predict/trajectory', inputs),

  simulate: (inputs: UserInputs, nSim = 10000, years = 20, seed = 42) =>
    apiFetch<SimulationResponse>('/simulate', {
      inputs,
      n_simulations: nSim,
      years_horizon: years,
      random_seed: seed,
    }),

  explain: (inputs: UserInputs) =>
    apiFetch<ExplainResponse>('/explain', inputs),

  getAdvice: (inputs: UserInputs, question: string) =>
    apiFetch<AdviceResponse>('/advice', { inputs, question }),
};
