"""
Feature engineering module for ChronoPath (v2 — redesigned).

Transforms raw user inputs + dataset features into model-ready feature vectors.
All formulas and normalization choices are explicit and documented.

New in v2:
- 5 new raw features: skill_level, sleep_hours, social_media, risk_tolerance, side_project
- 2 new derived features: wellbeing_score, entrepreneurial_drive
- 7 industry sectors instead of tech-only job categories
- Constraint: years_experience ≤ age - 18
"""

import numpy as np
import pandas as pd
from typing import Dict, Any

# ─────────────────────────────────────────────────────
# 1. RAW FEATURE DEFINITIONS (from user sliders + data)
# ─────────────────────────────────────────────────────
RAW_FEATURES = [
    # Group 1: Personal Information
    "age",                        # int: 18–65
    "education_level",            # ordinal: 0=HS, 1=diploma, 2=bachelor, 3=master, 4=phd, 5=elite/MBA
    "years_experience",           # int: 0–47 (constrained: ≤ age - 18)
    "country",                    # categorical: ISO alpha-3 code

    # Group 2: Career Development
    "job_category",               # categorical: industry sector
    "skill_level",                # int: 0–10 (professional skill level)
    "study_hours_per_day",        # float: 0–6
    "networking_hours_per_week",  # float: 0–10

    # Group 3: Work Lifestyle
    "work_hours_per_week",        # float: 20–70
    "exercise_days_per_week",     # int: 0–7
    "sleep_hours_per_night",      # float: 4–10
    "social_media_hours_per_day", # float: 0–8

    # Group 4: Financial Behavior
    "savings_rate_pct",           # float: 0–60
    "risk_tolerance",             # int: 0–10
    "side_project_effort",        # int: 0–10
]

# ─────────────────────────────────────────────────────
# 2. DERIVED FEATURES — Formulas and pseudocode
# ─────────────────────────────────────────────────────

def compute_career_score(row: pd.Series) -> float:
    """
    Career score (0–100): weighted combination of education, experience,
    skill level, continuous learning, and networking.

    Formula:
      career_score = 0.20 * education_norm
                   + 0.25 * experience_norm
                   + 0.25 * skill_norm
                   + 0.15 * study_intensity
                   + 0.15 * networking_intensity
    """
    education_norm = row["education_level"] / 5.0 * 100
    experience_norm = min(row["years_experience"] / 30.0, 1.0) * 100
    skill_norm = row["skill_level"] / 10.0 * 100
    study_intensity = min(row["study_hours_per_day"] / 4.0, 1.0) * 100
    networking_intensity = min(row["networking_hours_per_week"] / 8.0, 1.0) * 100

    return (
        0.20 * education_norm
        + 0.25 * experience_norm
        + 0.25 * skill_norm
        + 0.15 * study_intensity
        + 0.15 * networking_intensity
    )


def compute_financial_discipline(row: pd.Series) -> float:
    """
    Financial discipline score (0–100): savings rate + risk-aware behavior.

    Formula:
      savings_norm = (savings_rate_pct / 60) * 100
      risk_adjustment = 50 + (risk_tolerance - 5) * 5  # centered at 50, ±25
      financial_discipline = 0.70 * savings_norm + 0.30 * risk_adjustment
    """
    savings_norm = (row["savings_rate_pct"] / 60.0) * 100
    risk_adjustment = 50 + (row["risk_tolerance"] - 5) * 5
    return np.clip(0.70 * savings_norm + 0.30 * risk_adjustment, 0, 100)


def compute_health_score(row: pd.Series) -> float:
    """
    Health score (0–100): exercise + sleep, penalized by overwork and excessive
    social media.

    Formula:
      exercise_norm = (exercise_days / 7) * 40
      sleep_quality = ((sleep_hours - 4) / 4) * 30    # 4h→0, 8h→30
      overwork_penalty = max(0, (work_hours - 40) / 30) * 20
      screen_penalty = max(0, (social_media_hours - 2) / 6) * 10
      health_score = clip(exercise_norm + sleep_quality - overwork_penalty - screen_penalty, 0, 100)
    """
    exercise_norm = (row["exercise_days_per_week"] / 7.0) * 40
    sleep_quality = max(0, (row["sleep_hours_per_night"] - 4) / 4.0) * 30
    overwork_penalty = max(0, (row["work_hours_per_week"] - 40) / 30.0) * 20
    screen_penalty = max(0, (row["social_media_hours_per_day"] - 2) / 6.0) * 10
    return np.clip(exercise_norm + sleep_quality - overwork_penalty - screen_penalty, 0, 100)


def compute_learning_rate(row: pd.Series) -> float:
    """
    Learning rate (0–1): diminishing returns model for study hours,
    boosted by education and skill level.

    Formula:
      raw_rate = 1 - exp(-0.5 * study_hours_per_day)
      education_boost = 1 + 0.08 * education_level
      skill_boost = 1 + 0.03 * skill_level
      learning_rate = clip(raw_rate * education_boost * skill_boost, 0, 1)
    """
    raw_rate = 1 - np.exp(-0.5 * row["study_hours_per_day"])
    education_boost = 1 + 0.08 * row["education_level"]
    skill_boost = 1 + 0.03 * row["skill_level"]
    return np.clip(raw_rate * education_boost * skill_boost, 0, 1)


def compute_wellbeing_score(row: pd.Series) -> float:
    """
    Wellbeing score (0–100): holistic measure combining sleep, exercise,
    work-life balance, and social media moderation.

    Formula:
      sleep_component = ((sleep_hours - 4) / 4) * 35       # 4h→0, 8h→35
      exercise_component = (exercise_days / 7) * 30
      balance_component = (1 - max(0, (work_hours - 40)/30)) * 20
      moderation_component = (1 - social_media / 8) * 15
      wellbeing = clip(sum, 0, 100)
    """
    sleep_c = max(0, (row["sleep_hours_per_night"] - 4) / 4.0) * 35
    exercise_c = (row["exercise_days_per_week"] / 7.0) * 30
    balance_c = max(0, 1 - max(0, (row["work_hours_per_week"] - 40) / 30.0)) * 20
    moderation_c = max(0, 1 - row["social_media_hours_per_day"] / 8.0) * 15
    return np.clip(sleep_c + exercise_c + balance_c + moderation_c, 0, 100)


def compute_entrepreneurial_drive(row: pd.Series) -> float:
    """
    Entrepreneurial drive (0–100): combination of risk tolerance,
    side project effort, and study intensity.

    Formula:
      risk_norm = (risk_tolerance / 10) * 40
      side_proj_norm = (side_project_effort / 10) * 40
      study_contrib = min(study_hours / 4, 1) * 20
      entrepreneurial_drive = clip(sum, 0, 100)
    """
    risk_norm = (row["risk_tolerance"] / 10.0) * 40
    side_proj_norm = (row["side_project_effort"] / 10.0) * 40
    study_contrib = min(row["study_hours_per_day"] / 4.0, 1.0) * 20
    return np.clip(risk_norm + side_proj_norm + study_contrib, 0, 100)


# ─────────────────────────────────────────────────────
# 3. CATEGORICAL ENCODING
# ─────────────────────────────────────────────────────

# Industry sectors → income tier (based on median salary)
JOB_CATEGORY_MAP = {
    "technology": 5,
    "finance": 5,
    "healthcare": 4,
    "entrepreneurship": 4,
    "creative_media": 3,
    "education": 2,
    "government": 2,
    "other": 3,
}

# Industry → stress multiplier (used in Monte Carlo)
JOB_STRESS_MAP = {
    "technology": 0.6,
    "finance": 0.8,
    "healthcare": 0.7,
    "entrepreneurship": 0.9,
    "creative_media": 0.4,
    "education": 0.3,
    "government": 0.3,
    "other": 0.5,
}

# Industry → growth rate bonus
JOB_GROWTH_MAP = {
    "technology": 0.015,
    "finance": 0.012,
    "healthcare": 0.010,
    "entrepreneurship": 0.020,
    "creative_media": 0.008,
    "education": 0.005,
    "government": 0.003,
    "other": 0.008,
}

# Country → income tier
COUNTRY_INCOME_TIER = {
    "USA": 4, "GBR": 3, "DEU": 3, "CAN": 3, "AUS": 3,
    "IND": 1, "BRA": 1, "NGA": 0, "other": 2,
}


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode categorical features into numeric representations.
    - job_category → ordinal via JOB_CATEGORY_MAP
    - country → income_tier via COUNTRY_INCOME_TIER
    """
    df = df.copy()
    df["job_category_encoded"] = (
        df["job_category"]
        .map(JOB_CATEGORY_MAP)
        .fillna(JOB_CATEGORY_MAP["other"])
        .astype(int)
    )
    df["country_income_tier"] = (
        df["country"]
        .map(COUNTRY_INCOME_TIER)
        .fillna(COUNTRY_INCOME_TIER["other"])
        .astype(int)
    )
    return df


# ─────────────────────────────────────────────────────
# 4. NORMALIZATION
# ─────────────────────────────────────────────────────

CONTINUOUS_FEATURES = [
    "age", "years_experience", "study_hours_per_day",
    "work_hours_per_week", "savings_rate_pct",
    "exercise_days_per_week", "networking_hours_per_week",
    "skill_level", "sleep_hours_per_night",
    "social_media_hours_per_day", "risk_tolerance", "side_project_effort",
]

FEATURE_RANGES = {
    "age": (18, 65),
    "years_experience": (0, 47),
    "study_hours_per_day": (0, 6),
    "work_hours_per_week": (20, 70),
    "savings_rate_pct": (0, 60),
    "exercise_days_per_week": (0, 7),
    "networking_hours_per_week": (0, 10),
    "skill_level": (0, 10),
    "sleep_hours_per_night": (4, 10),
    "social_media_hours_per_day": (0, 8),
    "risk_tolerance": (0, 10),
    "side_project_effort": (0, 10),
}


def normalize_features(df: pd.DataFrame) -> pd.DataFrame:
    """Min-max normalize continuous features to [0, 1]."""
    df = df.copy()
    for feature, (lo, hi) in FEATURE_RANGES.items():
        if feature in df.columns:
            df[f"{feature}_norm"] = (df[feature] - lo) / (hi - lo)
    return df


# ─────────────────────────────────────────────────────
# 5. IMPUTATION
# ─────────────────────────────────────────────────────

def impute_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy:
    - Continuous features: median imputation (robust to outliers)
    - Categorical features: mode imputation
    - Ordinal features: median imputation (preserves ordering)
    """
    df = df.copy()

    for col in CONTINUOUS_FEATURES:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    for col in ["job_category", "country"]:
        if col in df.columns and df[col].isna().any():
            df[col] = df[col].fillna(df[col].mode().iloc[0])

    for col in ["education_level"]:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    return df


# ─────────────────────────────────────────────────────
# 6. CONSTRAINT ENFORCEMENT
# ─────────────────────────────────────────────────────

def enforce_constraints(df: pd.DataFrame) -> pd.DataFrame:
    """Apply logical constraints between variables."""
    df = df.copy()
    # years_experience ≤ age - 18
    if "age" in df.columns and "years_experience" in df.columns:
        max_exp = df["age"] - 18
        df["years_experience"] = df[["years_experience"]].clip(upper=max_exp, axis=0).iloc[:, 0]
    return df


# ─────────────────────────────────────────────────────
# 7. FULL PIPELINE: Raw → Model-Ready
# ─────────────────────────────────────────────────────

FINAL_FEATURE_COLUMNS = [
    # Normalized continuous
    "age_norm", "years_experience_norm", "study_hours_per_day_norm",
    "work_hours_per_week_norm", "savings_rate_pct_norm",
    "exercise_days_per_week_norm", "networking_hours_per_week_norm",
    "skill_level_norm", "sleep_hours_per_night_norm",
    "social_media_hours_per_day_norm", "risk_tolerance_norm",
    "side_project_effort_norm",
    # Ordinal / encoded
    "education_level",
    "job_category_encoded", "country_income_tier",
    # Derived
    "career_score", "financial_discipline", "health_score",
    "learning_rate", "wellbeing_score", "entrepreneurial_drive",
]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    End-to-end feature pipeline:
    1. Enforce constraints
    2. Impute missing values
    3. Encode categoricals
    4. Normalize continuous features
    5. Compute derived features
    6. Return model-ready DataFrame with FINAL_FEATURE_COLUMNS
    """
    df = enforce_constraints(df)
    df = impute_missing(df)
    df = encode_categoricals(df)
    df = normalize_features(df)

    # Derived features
    df["career_score"] = df.apply(compute_career_score, axis=1)
    df["financial_discipline"] = df.apply(compute_financial_discipline, axis=1)
    df["health_score"] = df.apply(compute_health_score, axis=1)
    df["learning_rate"] = df.apply(compute_learning_rate, axis=1)
    df["wellbeing_score"] = df.apply(compute_wellbeing_score, axis=1)
    df["entrepreneurial_drive"] = df.apply(compute_entrepreneurial_drive, axis=1)

    return df[FINAL_FEATURE_COLUMNS]


def user_input_to_feature_vector(user_input: Dict[str, Any]) -> np.ndarray:
    """
    Convert a single user input dict (from API request) to a
    model-ready feature vector.
    """
    df = pd.DataFrame([user_input])
    features = build_features(df)
    return features.values[0]
