"""
Pydantic models (request/response schemas) for the ChronoPath API.
"""

from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Optional


# ─────────────────────────────────────────────────────
# REQUEST SCHEMAS
# ─────────────────────────────────────────────────────

class UserInputs(BaseModel):
    """User's life decision inputs — matches the frontend sliders."""

    # GROUP 1: Personal Information
    age: int = Field(28, ge=18, le=65, description="Current age")
    education_level: int = Field(3, ge=0, le=5,
        description="0=High School, 1=Diploma, 2=Bachelor's, 3=Master's, 4=PhD, 5=Elite/MBA")
    years_experience: int = Field(5, ge=0, le=47, description="Years of professional experience")
    country: str = Field("USA", description="ISO country code")

    # GROUP 2: Career Development
    job_category: str = Field("technology", description="Industry sector slug")
    skill_level: int = Field(6, ge=0, le=10,
        description="Current professional skill level (0=beginner, 10=world-class)")
    study_hours_per_day: float = Field(2.0, ge=0, le=6, description="Daily study/learning hours")
    networking_hours_per_week: float = Field(4.0, ge=0, le=10,
        description="Weekly professional networking hours")

    # GROUP 3: Work Lifestyle
    work_hours_per_week: float = Field(40.0, ge=20, le=70, description="Weekly work hours")
    exercise_days_per_week: int = Field(3, ge=0, le=7, description="Days per week of exercise")
    sleep_hours_per_night: float = Field(7.0, ge=4, le=10,
        description="Average sleep hours per night")
    social_media_hours_per_day: float = Field(2.0, ge=0, le=8,
        description="Daily recreational social media hours")

    # GROUP 4: Financial Behavior
    savings_rate_pct: float = Field(20.0, ge=0, le=60, description="Percentage of income saved")
    risk_tolerance: int = Field(5, ge=0, le=10,
        description="Financial risk tolerance (0=very conservative, 10=very aggressive)")
    side_project_effort: int = Field(3, ge=0, le=10,
        description="Effort on side projects / entrepreneurship (0=none, 10=full hustle)")

    @model_validator(mode="after")
    def enforce_constraints(self):
        """years_experience must be ≤ age - 18"""
        max_exp = self.age - 18
        if self.years_experience > max_exp:
            self.years_experience = max_exp
        return self

    model_config = {"json_schema_extra": {
        "examples": [{
            "age": 28, "education_level": 3, "years_experience": 5,
            "country": "USA", "job_category": "technology", "skill_level": 6,
            "study_hours_per_day": 2.0, "networking_hours_per_week": 4.0,
            "work_hours_per_week": 40.0, "exercise_days_per_week": 3,
            "sleep_hours_per_night": 7.0, "social_media_hours_per_day": 2.0,
            "savings_rate_pct": 20.0, "risk_tolerance": 5, "side_project_effort": 3,
        }]
    }}


class SimulateRequest(BaseModel):
    """Request body for /simulate endpoint."""
    inputs: UserInputs
    n_simulations: int = Field(10000, ge=100, le=100000, description="Number of Monte Carlo runs")
    years_horizon: int = Field(20, ge=1, le=30, description="Years to simulate")
    random_seed: int = Field(42, description="Random seed for reproducibility")


class AdviceRequest(BaseModel):
    """Request body for /advice (AI Career Coach) endpoint."""
    inputs: UserInputs
    question: str = Field(
        ...,
        description="User's question for the AI Career Coach",
        min_length=5,
        max_length=500,
    )


# ─────────────────────────────────────────────────────
# RESPONSE SCHEMAS
# ─────────────────────────────────────────────────────

class TrajectoryResponse(BaseModel):
    """Response from /predict/trajectory — deterministic single-path prediction."""
    predicted_income: float = Field(description="Predicted annual income (USD)")
    predicted_happiness: float = Field(description="Predicted happiness score (0-10)")
    predicted_stress_probability: float = Field(description="Probability of high stress (0-1)")
    confidence_intervals: Dict[str, Dict[str, float]] = Field(
        description="95% confidence intervals for each prediction"
    )
    feature_importances: Dict[str, float] = Field(
        description="Top feature importances from the income model"
    )


class PercentileData(BaseModel):
    """Percentile bands for a single metric across time."""
    percentiles: Dict[int, List[float]] = Field(
        description="Percentile → list of values per year"
    )
    sample_trajectories: List[List[float]] = Field(
        description="5 sample trajectories for spaghetti plot"
    )


class SimulateResponse(BaseModel):
    """Response from /simulate — Monte Carlo percentile distributions."""
    years: List[int]
    income: PercentileData
    happiness: PercentileData
    stress: PercentileData
    config: Dict[str, object] = Field(description="Simulation config used")


class ExplainResponse(BaseModel):
    """Response from /explain — SHAP feature contributions."""
    base_value: float = Field(description="Model's expected (average) prediction")
    prediction: float = Field(description="Actual prediction for this input")
    contributions: List[Dict[str, object]] = Field(
        description="Ordered list of {feature, value, shap_value, direction}"
    )


class AdviceResponse(BaseModel):
    """Response from /advice — AI Career Coach output."""
    answer: str = Field(description="Coach's textual advice")
    action_items: List[Dict[str, str]] = Field(
        description="Prioritized action items with estimated impact"
    )
    top_factors: List[str] = Field(
        description="Top 3 SHAP features driving the prediction"
    )
