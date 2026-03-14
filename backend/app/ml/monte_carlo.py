"""
Monte Carlo simulation engine for ChronoPath (v2 — redesigned).

Incorporates new variables: skill_level, sleep, social_media, risk_tolerance,
side_project_effort into the growth/happiness/stress models.

Noise model: Gaussian perturbation based on model residuals (RMSE from validation).
All random seeds are explicit for reproducibility.
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass


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

# Industry-specific stress multipliers
JOB_STRESS_MULT = {
    "technology": 0.6,
    "finance": 0.8,
    "healthcare": 0.7,
    "entrepreneurship": 0.9,
    "creative_media": 0.4,
    "education": 0.3,
    "government": 0.3,
}


@dataclass
class SimulationConfig:
    """Configuration for Monte Carlo simulation."""
    n_simulations: int = 10_000
    years_horizon: int = 20
    random_seed: int = 42
    income_growth_base: float = 0.03   # 3% annual baseline growth
    income_noise_std: float = 0.12     # Std dev of income noise
    happiness_noise_std: float = 0.8   # Std dev on 0-10 scale
    stress_noise_std: float = 0.10     # Std dev for stress probability


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
    skill_boost = user_features.get("skill_level", 5) * 0.004          # NEW: +0.4% per skill level
    side_project_boost = user_features.get("side_project_effort", 0) * 0.003  # NEW: +0.3% per effort unit

    # Industry-specific growth bonus
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
    # NEW: sleep contributes positively (optimal ~7-8h, penalty below 6h)
    sleep_hrs = user_features.get("sleep_hours_per_night", 7)
    sleep_effect = min(0.3, max(-0.5, (sleep_hrs - 6) * 0.15))
    # NEW: excessive social media reduces happiness
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

    # ── STRESS SIMULATION ──
    work_pressure = user_features.get("work_hours_per_week", 40) / 70.0 * 0.01
    # NEW: sleep deficit increases stress
    sleep_deficit_pressure = max(0, (7 - sleep_hrs) * 0.02)
    # NEW: industry stress multiplier
    industry_stress = JOB_STRESS_MULT.get(job_cat, 0.5) * 0.005
    # NEW: risk tolerance slightly increases stress (high-stakes decisions)
    risk_stress = user_features.get("risk_tolerance", 5) * 0.002
    # NEW: exercise reduces stress accumulation
    exercise_relief = user_features.get("exercise_days_per_week", 3) * (-0.003)

    stress_noise = rng.normal(
        loc=0,
        scale=config.stress_noise_std,
        size=(config.n_simulations, config.years_horizon),
    )
    stress_trajectories = np.zeros((config.n_simulations, config.years_horizon))
    for t in range(config.years_horizon):
        pressure = (work_pressure + sleep_deficit_pressure + industry_stress + risk_stress + exercise_relief) * (t + 1) * 0.5
        stress_trajectories[:, t] = base_stress_probability + pressure + stress_noise[:, t]

    stress_trajectories = np.clip(stress_trajectories, 0, 1)

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
