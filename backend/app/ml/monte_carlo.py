"""
Monte Carlo simulation engine for ChronoPath (v3 — calibrated stress).

Key change in v3: stress probabilities now use a sigmoid (logistic) transformation
instead of raw linear scores. This ensures:
  - probabilities are smooth and asymptotically bounded
  - output never reaches exactly 0% or 100%
  - final range is clamped to [5%, 95%] for realism

Noise model: Gaussian perturbation based on model residuals (RMSE from validation).
All random seeds are explicit for reproducibility.
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass


# ── Constants ──

# Industry-specific growth rate bonuses
JOB_GROWTH_RATES = {
    "technology": 0.015,
    "finance": 0.012,
    "healthcare": 0.010,
    "entrepreneurship": 0.020,
    "creative_media": 0.008,
    "education": 0.005,
    "government": 0.003,
}

# Industry-specific stress multipliers (contribution to logit score)
JOB_STRESS_MULT = {
    "technology": 0.6,
    "finance": 0.8,
    "healthcare": 0.7,
    "entrepreneurship": 0.9,
    "creative_media": 0.4,
    "education": 0.3,
    "government": 0.3,
}

# Stress probability floor/ceiling
STRESS_PROB_MIN = 0.05
STRESS_PROB_MAX = 0.95


def _sigmoid(x: np.ndarray) -> np.ndarray:
    """Numerically stable sigmoid function."""
    return np.where(
        x >= 0,
        1.0 / (1.0 + np.exp(-x)),
        np.exp(x) / (1.0 + np.exp(x)),
    )


def _logit(p: float) -> float:
    """Inverse sigmoid — convert probability to log-odds."""
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(np.log(p / (1 - p)))


@dataclass
class SimulationConfig:
    """Configuration for Monte Carlo simulation."""
    n_simulations: int = 10_000
    years_horizon: int = 20
    random_seed: int = 42
    income_growth_base: float = 0.03   # 3% annual baseline growth
    income_noise_std: float = 0.12     # Std dev of income noise
    happiness_noise_std: float = 0.8   # Std dev on 0-10 scale
    stress_logit_noise_std: float = 0.35  # Noise in logit space (wider but bounded by sigmoid)


def run_monte_carlo(
    base_income_prediction: float,
    base_happiness_prediction: float,
    base_stress_probability: float,
    user_features: Dict[str, float],
    config: Optional[SimulationConfig] = None,
) -> Dict[str, np.ndarray]:
    """
    Run Monte Carlo simulation for life trajectory predictions.

    Parameters
    ----------
    base_income_prediction : float
        Model-predicted current annual income (USD).
    base_happiness_prediction : float
        Model-predicted happiness score (0-10 scale).
    base_stress_probability : float
        Model-predicted probability of high stress (0-1).
    user_features : dict
        User's input features (used for growth rate adjustments).
    config : SimulationConfig, optional
        Simulation parameters. Uses defaults if None.

    Returns
    -------
    dict with percentiles, sample trajectories, and years.
    """
    if config is None:
        config = SimulationConfig()

    rng = np.random.default_rng(seed=config.random_seed)
    years = np.arange(1, config.years_horizon + 1)

    # ── GROWTH RATE ADJUSTMENTS ──
    study_boost = user_features.get("study_hours_per_day", 0) * 0.005
    network_boost = user_features.get("networking_hours_per_week", 0) * 0.003
    education_boost = user_features.get("education_level", 2) * 0.008
    savings_compound = user_features.get("savings_rate_pct", 10) * 0.0008
    skill_boost = user_features.get("skill_level", 5) * 0.004
    side_project_boost = user_features.get("side_project_effort", 0) * 0.003

    job_cat = user_features.get("job_category", "technology")
    industry_boost = JOB_GROWTH_RATES.get(job_cat, 0.008)

    effective_growth_rate = (
        config.income_growth_base
        + study_boost
        + network_boost
        + education_boost
        + savings_compound
        + skill_boost
        + side_project_boost
        + industry_boost
    )

    # ── INCOME SIMULATION ──
    income_noise = rng.normal(
        loc=0,
        scale=config.income_noise_std,
        size=(config.n_simulations, config.years_horizon),
    )
    income_trajectories = np.zeros((config.n_simulations, config.years_horizon))
    for t in range(config.years_horizon):
        if t == 0:
            growth_factor = 1 + effective_growth_rate + income_noise[:, t]
            income_trajectories[:, t] = base_income_prediction * growth_factor
        else:
            growth_factor = 1 + effective_growth_rate + income_noise[:, t]
            income_trajectories[:, t] = income_trajectories[:, t - 1] * growth_factor

    income_trajectories = np.maximum(income_trajectories, 0)

    # ── HAPPINESS SIMULATION ──
    exercise_effect = user_features.get("exercise_days_per_week", 3) * 0.05
    overwork_effect = max(0, user_features.get("work_hours_per_week", 40) - 40) * (-0.02)
    sleep_hrs = user_features.get("sleep_hours_per_night", 7)
    sleep_effect = min(0.3, max(-0.5, (sleep_hrs - 6) * 0.15))
    social_media = user_features.get("social_media_hours_per_day", 2)
    social_media_effect = max(0, social_media - 2) * (-0.05)

    happiness_drift_per_year = exercise_effect + overwork_effect + sleep_effect + social_media_effect
    happiness_noise = rng.normal(
        loc=0,
        scale=config.happiness_noise_std,
        size=(config.n_simulations, config.years_horizon),
    )
    happiness_trajectories = np.zeros((config.n_simulations, config.years_horizon))
    for t in range(config.years_horizon):
        drift = happiness_drift_per_year * (t + 1) * 0.1
        happiness_trajectories[:, t] = base_happiness_prediction + drift + happiness_noise[:, t]

    happiness_trajectories = np.clip(happiness_trajectories, 0, 10)

    # ──────────────────────────────────────────────────────────────────
    # STRESS SIMULATION — Sigmoid-calibrated probabilities
    #
    # How it works:
    #   1. Convert the base stress probability to logit (log-odds) space.
    #   2. Compute normalized stress factors (each in [0, 1]).
    #   3. Combine them as weighted contributions to the logit score.
    #   4. Add Gaussian noise in logit space (noise stays bounded after sigmoid).
    #   5. Apply sigmoid → smooth probability in (0, 1).
    #   6. Clamp to [5%, 95%] for presentation realism.
    #
    # This ensures stress scales gradually and never reaches 0% or 100%,
    # even under extreme combinations of high-stress inputs.
    # ──────────────────────────────────────────────────────────────────

    # Step 1: Convert base probability to logit space
    base_logit = _logit(base_stress_probability)

    # Step 2: Normalize stress-driving features to [0, 1]
    work_hours = user_features.get("work_hours_per_week", 40)
    exercise_days = user_features.get("exercise_days_per_week", 3)
    risk_tol = user_features.get("risk_tolerance", 5)
    study_hours = user_features.get("study_hours_per_day", 2)

    work_norm = np.clip((work_hours - 20) / 50.0, 0, 1)         # 20-70 hrs → [0, 1]
    sleep_deficit_norm = np.clip((7 - sleep_hrs) / 3.0, 0, 1)    # 7h = 0, 4h = 1
    exercise_norm = np.clip(exercise_days / 7.0, 0, 1)           # 0-7 → [0, 1]
    social_norm = np.clip(social_media / 8.0, 0, 1)              # 0-8 → [0, 1]
    risk_norm = np.clip(risk_tol / 10.0, 0, 1)                   # 0-10 → [0, 1]
    study_overload_norm = np.clip((study_hours - 3) / 3.0, 0, 1) # >3h starts adding stress
    industry_mult = JOB_STRESS_MULT.get(job_cat, 0.5)            # already [0, 1]

    # Step 3: Weighted logit contributions (positive = more stress, negative = less)
    # Weights tuned so that even with ALL factors maxed, the logit score
    # tops out around +3 (sigmoid(+3) ≈ 95%) rather than infinity.
    logit_contribution = (
        work_norm * 1.2                  # heavy work is the biggest stress driver
        + sleep_deficit_norm * 0.9       # sleep loss is second-biggest
        + industry_mult * 0.5            # high-stress industries add pressure
        + social_norm * 0.3              # excessive social media adds distraction stress
        + risk_norm * 0.25               # high financial risk adds anxiety
        + study_overload_norm * 0.2      # excessive study adds to overwhelm
        - exercise_norm * 0.7            # exercise is the best stress reliever
    )

    # Step 4: Simulate in logit space with noise
    stress_noise = rng.normal(
        loc=0,
        scale=config.stress_logit_noise_std,
        size=(config.n_simulations, config.years_horizon),
    )

    stress_trajectories = np.zeros((config.n_simulations, config.years_horizon))
    for t in range(config.years_horizon):
        # Time-dependent pressure accumulation (logarithmic, not linear)
        # This prevents late-year scores from exploding
        time_drift = logit_contribution * np.log1p(t + 1) * 0.3

        # Raw logit score = base + lifestyle adjustment + time drift + noise
        raw_logit = base_logit + logit_contribution + time_drift + stress_noise[:, t]

        # Step 5: Sigmoid transformation → probability in (0, 1)
        prob = _sigmoid(raw_logit)

        # Step 6: Clamp to [5%, 95%]
        stress_trajectories[:, t] = np.clip(prob, STRESS_PROB_MIN, STRESS_PROB_MAX)

    # ── COMPUTE PERCENTILES ──
    percentile_keys = [5, 25, 50, 75, 95]

    def compute_percentiles(trajectories: np.ndarray) -> Dict[int, List[float]]:
        return {
            p: np.percentile(trajectories, p, axis=0).tolist()
            for p in percentile_keys
        }

    return {
        "years": years.tolist(),
        "income_trajectories": income_trajectories,
        "income_percentiles": compute_percentiles(income_trajectories),
        "happiness_trajectories": happiness_trajectories,
        "happiness_percentiles": compute_percentiles(happiness_trajectories),
        "stress_trajectories": stress_trajectories,
        "stress_percentiles": compute_percentiles(stress_trajectories),
        "income_samples": income_trajectories[:5].tolist(),
        "happiness_samples": happiness_trajectories[:5].tolist(),
        "stress_samples": stress_trajectories[:5].tolist(),
    }


def simulation_to_api_response(sim_results: Dict) -> Dict:
    """Convert simulation results to JSON-serializable API response."""
    return {
        "years": sim_results["years"],
        "income": {
            "percentiles": sim_results["income_percentiles"],
            "sample_trajectories": sim_results["income_samples"],
        },
        "happiness": {
            "percentiles": sim_results["happiness_percentiles"],
            "sample_trajectories": sim_results["happiness_samples"],
        },
        "stress": {
            "percentiles": sim_results["stress_percentiles"],
            "sample_trajectories": sim_results["stress_samples"],
        },
        "config": {
            "n_simulations": 10_000,
            "random_seed": 42,
            "noise_model": "gaussian_residual",
        },
    }


if __name__ == "__main__":
    sample_features = {
        "age": 28, "education_level": 3, "years_experience": 5,
        "study_hours_per_day": 2.0, "work_hours_per_week": 40,
        "savings_rate_pct": 20, "exercise_days_per_week": 3,
        "networking_hours_per_week": 4, "skill_level": 6,
        "sleep_hours_per_night": 7, "social_media_hours_per_day": 2,
        "risk_tolerance": 5, "side_project_effort": 3,
        "job_category": "technology",
    }

    results = run_monte_carlo(
        base_income_prediction=75000,
        base_happiness_prediction=6.5,
        base_stress_probability=0.35,
        user_features=sample_features,
    )
    api_resp = simulation_to_api_response(results)

    print("=== Monte Carlo Results (Year 10) ===")
    print(f"Income 5th–95th: ${api_resp['income']['percentiles'][5][9]:,.0f}"
          f" – ${api_resp['income']['percentiles'][95][9]:,.0f}")
    print(f"Income median:   ${api_resp['income']['percentiles'][50][9]:,.0f}")
    print(f"Happiness median: {api_resp['happiness']['percentiles'][50][9]:.1f}/10")
    print(f"Stress median:    {api_resp['stress']['percentiles'][50][9]:.0%}")
