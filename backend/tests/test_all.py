"""
Tests for ChronoPath (v2 — redesigned with 15 variables).
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ml.feature_engineering import (
    build_features, user_input_to_feature_vector,
    compute_career_score, compute_health_score,
    compute_wellbeing_score, compute_entrepreneurial_drive,
    FINAL_FEATURE_COLUMNS,
)
from app.ml.monte_carlo import run_monte_carlo, SimulationConfig

import pandas as pd


# ─── Sample inputs matching new schema ───
SAMPLE_INPUTS = {
    "age": 28, "education_level": 3, "years_experience": 5,
    "country": "USA", "job_category": "technology", "skill_level": 6,
    "study_hours_per_day": 2.0, "networking_hours_per_week": 4.0,
    "work_hours_per_week": 40.0, "exercise_days_per_week": 3,
    "sleep_hours_per_night": 7.0, "social_media_hours_per_day": 2.0,
    "savings_rate_pct": 20.0, "risk_tolerance": 5, "side_project_effort": 3,
}


class TestFeatureEngineering:
    """Tests for feature_engineering.py"""

    def test_user_input_to_feature_vector_shape(self):
        """Feature vector should have correct number of features."""
        vec = user_input_to_feature_vector(SAMPLE_INPUTS)
        assert len(vec) == len(FINAL_FEATURE_COLUMNS), \
            f"Expected {len(FINAL_FEATURE_COLUMNS)} features, got {len(vec)}"

    def test_build_features_columns(self):
        """build_features should return exactly FINAL_FEATURE_COLUMNS."""
        df = pd.DataFrame([SAMPLE_INPUTS])
        result = build_features(df)
        assert list(result.columns) == FINAL_FEATURE_COLUMNS

    def test_career_score_range(self):
        """Career score should be in [0, 100]."""
        row = pd.Series(SAMPLE_INPUTS)
        score = compute_career_score(row)
        assert 0 <= score <= 100, f"Career score {score} out of range"

    def test_health_score_range(self):
        """Health score should be in [0, 100]."""
        row = pd.Series(SAMPLE_INPUTS)
        score = compute_health_score(row)
        assert 0 <= score <= 100, f"Health score {score} out of range"

    def test_wellbeing_score_range(self):
        """Wellbeing score should be in [0, 100]."""
        row = pd.Series(SAMPLE_INPUTS)
        score = compute_wellbeing_score(row)
        assert 0 <= score <= 100, f"Wellbeing score {score} out of range"

    def test_entrepreneurial_drive_range(self):
        """Entrepreneurial drive should be in [0, 100]."""
        row = pd.Series(SAMPLE_INPUTS)
        score = compute_entrepreneurial_drive(row)
        assert 0 <= score <= 100, f"Entrepreneurial drive {score} out of range"

    def test_experience_constraint(self):
        """years_experience should be clamped to age - 18."""
        inputs = {**SAMPLE_INPUTS, "age": 22, "years_experience": 10}
        df = pd.DataFrame([inputs])
        result = build_features(df)
        # Should have processed without error (constraint caps to 4)
        assert result.shape[0] == 1

    def test_normalization_bounds(self):
        """Normalized features should be in [0, 1]."""
        vec = user_input_to_feature_vector(SAMPLE_INPUTS)
        df = pd.DataFrame([SAMPLE_INPUTS])
        result = build_features(df)
        norm_cols = [c for c in result.columns if c.endswith("_norm")]
        for col in norm_cols:
            val = result[col].iloc[0]
            assert 0 <= val <= 1, f"{col} = {val} is outside [0, 1]"


class TestMonteCarlo:
    """Tests for monte_carlo.py"""

    def test_deterministic_with_seed(self):
        """Same seed should produce identical results."""
        config = SimulationConfig(n_simulations=100, years_horizon=5, random_seed=42)
        r1 = run_monte_carlo(75000, 6.5, 0.35, SAMPLE_INPUTS, config)
        r2 = run_monte_carlo(75000, 6.5, 0.35, SAMPLE_INPUTS, config)
        np.testing.assert_array_almost_equal(
            r1["income_percentiles"][50],
            r2["income_percentiles"][50],
        )

    def test_output_shape(self):
        """Output trajectories should have correct shape."""
        config = SimulationConfig(n_simulations=100, years_horizon=10, random_seed=42)
        results = run_monte_carlo(75000, 6.5, 0.35, SAMPLE_INPUTS, config)
        assert results["income_trajectories"].shape == (100, 10)
        assert results["happiness_trajectories"].shape == (100, 10)
        assert results["stress_trajectories"].shape == (100, 10)

    def test_income_non_negative(self):
        """All income values should be >= 0."""
        config = SimulationConfig(n_simulations=500, years_horizon=5, random_seed=42)
        results = run_monte_carlo(75000, 6.5, 0.35, SAMPLE_INPUTS, config)
        assert np.all(results["income_trajectories"] >= 0)

    def test_happiness_bounded(self):
        """Happiness should be in [0, 10]."""
        config = SimulationConfig(n_simulations=500, years_horizon=5, random_seed=42)
        results = run_monte_carlo(75000, 6.5, 0.35, SAMPLE_INPUTS, config)
        assert np.all(results["happiness_trajectories"] >= 0)
        assert np.all(results["happiness_trajectories"] <= 10)

    def test_stress_bounded(self):
        """Stress probability should be in [0, 1]."""
        config = SimulationConfig(n_simulations=500, years_horizon=5, random_seed=42)
        results = run_monte_carlo(75000, 6.5, 0.35, SAMPLE_INPUTS, config)
        assert np.all(results["stress_trajectories"] >= 0)
        assert np.all(results["stress_trajectories"] <= 1)

    def test_percentiles_ordered(self):
        """Percentiles should be ordered: p5 ≤ p25 ≤ p50 ≤ p75 ≤ p95."""
        config = SimulationConfig(n_simulations=1000, years_horizon=5, random_seed=42)
        results = run_monte_carlo(75000, 6.5, 0.35, SAMPLE_INPUTS, config)
        for t in range(5):
            p5 = results["income_percentiles"][5][t]
            p25 = results["income_percentiles"][25][t]
            p50 = results["income_percentiles"][50][t]
            p75 = results["income_percentiles"][75][t]
            p95 = results["income_percentiles"][95][t]
            assert p5 <= p25 <= p50 <= p75 <= p95

    def test_skill_boost_effect(self):
        """Higher skill_level should increase median income."""
        config = SimulationConfig(n_simulations=1000, years_horizon=10, random_seed=42)
        low_skill = {**SAMPLE_INPUTS, "skill_level": 2}
        high_skill = {**SAMPLE_INPUTS, "skill_level": 9}
        r_low = run_monte_carlo(75000, 6.5, 0.35, low_skill, config)
        r_high = run_monte_carlo(75000, 6.5, 0.35, high_skill, config)
        assert r_high["income_percentiles"][50][-1] > r_low["income_percentiles"][50][-1]


class TestAPIEndpoints:
    """Smoke tests for FastAPI endpoints."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        """Set up test client with model loading."""
        from app.main import app
        from app.ml.model_loader import registry, MODEL_DIR
        from fastapi.testclient import TestClient

        if not (MODEL_DIR / "income_xgboost.joblib").exists():
            pytest.skip("Models not trained yet (run train_models.py first)")

        registry.load_all()
        self.client = TestClient(app)

    def test_predict_trajectory(self):
        resp = self.client.post("/predict/trajectory", json=SAMPLE_INPUTS)
        assert resp.status_code == 200
        data = resp.json()
        assert "predicted_income" in data
        assert data["predicted_income"] > 0
        assert 0 <= data["predicted_happiness"] <= 10
        assert 0 <= data["predicted_stress_probability"] <= 1

    def test_simulate(self):
        resp = self.client.post("/simulate", json={
            "inputs": SAMPLE_INPUTS,
            "n_simulations": 100,
            "years_horizon": 5,
            "random_seed": 42,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["years"]) == 5
        assert "50" in data["income"]["percentiles"]

    def test_explain(self):
        resp = self.client.post("/explain", json=SAMPLE_INPUTS)
        assert resp.status_code == 200
        data = resp.json()
        assert "contributions" in data

    def test_health_check(self):
        resp = self.client.get("/health")
        assert resp.status_code == 200
