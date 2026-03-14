"""
End-to-end training pipeline for ChronoPath (v2 — redesigned).

Trains three models with the expanded 15-variable input set:
1. Income Prediction (XGBoost Regressor)
2. Happiness Prediction (GradientBoosting Regressor)
3. Stress Classification (Logistic Regression, calibrated)

Run: python scripts/train_models.py
"""

import numpy as np
import pandas as pd
import joblib
import json
from pathlib import Path
from sklearn.model_selection import GroupKFold, cross_val_score
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss
import xgboost as xgb

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.ml.feature_engineering import build_features, FINAL_FEATURE_COLUMNS

RANDOM_SEED = 42
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_DIR.mkdir(exist_ok=True)
np.random.seed(RANDOM_SEED)


def generate_synthetic_dataset(n_samples: int = 5000) -> pd.DataFrame:
    """Generate a realistic synthetic dataset with all 15 input variables."""
    rng = np.random.default_rng(seed=RANDOM_SEED)
    n = n_samples

    ages = rng.integers(18, 65, size=n)

    df = pd.DataFrame({
        # Group 1: Personal Information
        "age": ages,
        "education_level": rng.choice([0, 1, 2, 3, 4, 5], size=n,
                                       p=[0.05, 0.10, 0.35, 0.30, 0.15, 0.05]),
        "years_experience": np.minimum(rng.integers(0, 40, size=n), ages - 18),
        "country": rng.choice(["USA", "GBR", "DEU", "IND", "CAN", "BRA", "AUS"],
                               size=n, p=[0.35, 0.10, 0.10, 0.20, 0.08, 0.10, 0.07]),

        # Group 2: Career Development
        "job_category": rng.choice(
            ["technology", "finance", "healthcare", "education",
             "government", "creative_media", "entrepreneurship"],
            size=n, p=[0.30, 0.15, 0.12, 0.10, 0.08, 0.12, 0.13]),
        "skill_level": rng.integers(1, 10, size=n),
        "study_hours_per_day": rng.uniform(0, 5, size=n).round(1),
        "networking_hours_per_week": rng.uniform(0, 8, size=n).round(1),

        # Group 3: Work Lifestyle
        "work_hours_per_week": rng.normal(42, 8, size=n).clip(20, 70).round(1),
        "exercise_days_per_week": rng.integers(0, 7, size=n),
        "sleep_hours_per_night": rng.normal(7, 1, size=n).clip(4, 10).round(1),
        "social_media_hours_per_day": rng.exponential(2, size=n).clip(0, 8).round(1),

        # Group 4: Financial Behavior
        "savings_rate_pct": rng.uniform(0, 50, size=n).round(1),
        "risk_tolerance": rng.integers(0, 10, size=n),
        "side_project_effort": rng.integers(0, 10, size=n),
    })

    # ── GENERATE TARGETS ──
    job_tier = df["job_category"].map({
        "technology": 5, "finance": 5, "healthcare": 4,
        "entrepreneurship": 4, "creative_media": 3,
        "education": 2, "government": 2,
    })
    country_mult = df["country"].map({
        "USA": 1.0, "GBR": 0.8, "DEU": 0.85, "CAN": 0.82,
        "AUS": 0.85, "IND": 0.25, "BRA": 0.30,
    })

    # Income
    df["annual_income_usd"] = (
        18000
        + df["education_level"] * 7000
        + df["years_experience"] * 2500
        + job_tier * 9000
        + df["skill_level"] * 4000
        + df["study_hours_per_day"] * 2500
        + df["side_project_effort"] * 1500
        + df["networking_hours_per_week"] * 800
    ) * country_mult + rng.normal(0, 8000, size=n)
    df["annual_income_usd"] = df["annual_income_usd"].clip(12000, 500000).round(0)

    # Happiness
    df["happiness_score"] = (
        3.5
        + df["exercise_days_per_week"] * 0.22
        + (df["sleep_hours_per_night"] - 6) * 0.4
        - np.maximum(0, df["work_hours_per_week"] - 40) * 0.035
        - np.maximum(0, df["social_media_hours_per_day"] - 2) * 0.12
        + df["networking_hours_per_week"] * 0.06
        + np.log1p(df["annual_income_usd"]) * 0.25
        + rng.normal(0, 0.7, size=n)
    ).clip(0, 10).round(2)

    # Stress (binary)
    stress_logit = (
        -2.5
        + 0.05 * df["work_hours_per_week"]
        - 0.15 * df["exercise_days_per_week"]
        - 0.2 * (df["sleep_hours_per_night"] - 6)
        + 0.08 * df["social_media_hours_per_day"]
        - 0.03 * df["savings_rate_pct"]
        + 0.06 * df["risk_tolerance"]
        + 0.05 * df["side_project_effort"]
        + rng.normal(0, 0.3, size=n)
    )
    stress_prob = 1 / (1 + np.exp(-stress_logit))
    df["high_stress"] = (stress_prob > 0.5).astype(int)

    return df


def prepare_data(df: pd.DataFrame):
    X = build_features(df)
    y_income = df["annual_income_usd"].values
    y_happiness = df["happiness_score"].values
    y_stress = df["high_stress"].values
    groups = df["country"].values
    return X, y_income, y_happiness, y_stress, groups


def train_income_model(X, y, groups):
    print("\n" + "=" * 60)
    print("INCOME MODEL TRAINING")
    print("=" * 60)

    gkf = GroupKFold(n_splits=5)

    XGBOOST_PARAMS = {
        "n_estimators": 500, "max_depth": 6, "learning_rate": 0.05,
        "subsample": 0.8, "colsample_bytree": 0.8, "min_child_weight": 5,
        "reg_alpha": 0.1, "reg_lambda": 1.0,
        "random_state": RANDOM_SEED, "n_jobs": -1,
    }

    xgb_model = xgb.XGBRegressor(**XGBOOST_PARAMS)

    xgb_rmse = -cross_val_score(xgb_model, X, y, cv=gkf, groups=groups,
                                 scoring="neg_root_mean_squared_error")
    xgb_r2 = cross_val_score(xgb_model, X, y, cv=gkf, groups=groups, scoring="r2")

    print(f"\n[Primary] XGBoost Regressor:")
    print(f"  CV RMSE: {xgb_rmse.mean():,.0f} ± {xgb_rmse.std():,.0f}")
    print(f"  CV R²:   {xgb_r2.mean():.4f} ± {xgb_r2.std():.4f}")

    xgb_model.fit(X, y)
    joblib.dump(xgb_model, MODEL_DIR / "income_xgboost.joblib")
    print(f"  ✓ Saved to {MODEL_DIR / 'income_xgboost.joblib'}")

    metadata = {
        "model": "XGBRegressor", "target": "annual_income_usd",
        "features": FINAL_FEATURE_COLUMNS,
        "cv_rmse_mean": float(xgb_rmse.mean()),
        "cv_r2_mean": float(xgb_r2.mean()),
        "hyperparameters": XGBOOST_PARAMS,
        "cv_scheme": "GroupKFold(n_splits=5, groups=country)",
        "random_seed": RANDOM_SEED,
    }
    with open(MODEL_DIR / "income_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    return xgb_model, metadata


def train_happiness_model(X, y, groups):
    print("\n" + "=" * 60)
    print("HAPPINESS MODEL TRAINING")
    print("=" * 60)

    GB_PARAMS = {
        "n_estimators": 300, "max_depth": 5, "learning_rate": 0.05,
        "subsample": 0.8, "min_samples_leaf": 10, "random_state": RANDOM_SEED,
    }
    gb_model = GradientBoostingRegressor(**GB_PARAMS)
    gkf = GroupKFold(n_splits=5)

    rmse = -cross_val_score(gb_model, X, y, cv=gkf, groups=groups,
                             scoring="neg_root_mean_squared_error")
    r2 = cross_val_score(gb_model, X, y, cv=gkf, groups=groups, scoring="r2")

    print(f"\n[Primary] GradientBoostingRegressor:")
    print(f"  CV RMSE: {rmse.mean():.3f} ± {rmse.std():.3f}")
    print(f"  CV R²:   {r2.mean():.4f} ± {r2.std():.4f}")

    gb_model.fit(X, y)
    joblib.dump(gb_model, MODEL_DIR / "happiness_gbr.joblib")
    print(f"  ✓ Saved to {MODEL_DIR / 'happiness_gbr.joblib'}")

    metadata = {
        "model": "GradientBoostingRegressor", "target": "happiness_score",
        "features": FINAL_FEATURE_COLUMNS,
        "cv_rmse_mean": float(rmse.mean()), "cv_r2_mean": float(r2.mean()),
        "hyperparameters": GB_PARAMS,
    }
    with open(MODEL_DIR / "happiness_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    return gb_model, metadata


def train_stress_model(X, y, groups):
    print("\n" + "=" * 60)
    print("STRESS MODEL TRAINING")
    print("=" * 60)

    lr_base = LogisticRegression(C=1.0, penalty="l2", max_iter=2000, random_state=RANDOM_SEED)
    calibrated_model = CalibratedClassifierCV(estimator=lr_base, method="sigmoid", cv=5)
    gkf = GroupKFold(n_splits=5)

    auc = cross_val_score(lr_base, X, y, cv=gkf, groups=groups, scoring="roc_auc")
    f1 = cross_val_score(lr_base, X, y, cv=gkf, groups=groups, scoring="f1")

    print(f"\n[Primary] Logistic Regression (calibrated):")
    print(f"  CV AUC-ROC: {auc.mean():.4f} ± {auc.std():.4f}")
    print(f"  CV F1:      {f1.mean():.4f} ± {f1.std():.4f}")

    calibrated_model.fit(X, y)
    y_prob = calibrated_model.predict_proba(X)[:, 1]
    brier = brier_score_loss(y, y_prob)
    print(f"  Brier Score: {brier:.4f}")

    joblib.dump(calibrated_model, MODEL_DIR / "stress_calibrated_lr.joblib")
    print(f"  ✓ Saved to {MODEL_DIR / 'stress_calibrated_lr.joblib'}")

    metadata = {
        "model": "CalibratedClassifierCV(LogisticRegression, method='sigmoid')",
        "target": "high_stress", "features": FINAL_FEATURE_COLUMNS,
        "cv_auc_mean": float(auc.mean()), "cv_f1_mean": float(f1.mean()),
        "brier_score_train": float(brier),
    }
    with open(MODEL_DIR / "stress_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    return calibrated_model, metadata


def generate_shap_summary(model, X, model_name: str = "income"):
    try:
        import shap
        if hasattr(model, "get_booster") or "GradientBoosting" in type(model).__name__:
            explainer = shap.TreeExplainer(model)
        elif hasattr(model, "estimator"):
            explainer = shap.LinearExplainer(model.estimator, X)
        else:
            explainer = shap.KernelExplainer(model.predict, X[:100])

        shap_values = explainer.shap_values(X[:200])
        np.save(MODEL_DIR / f"shap_values_{model_name}.npy", shap_values)
        print(f"  ✓ SHAP values saved for {model_name}")

        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        sorted_idx = np.argsort(mean_abs_shap)[::-1]
        print(f"\n  Top-5 features ({model_name}):")
        for i in sorted_idx[:5]:
            print(f"    {FINAL_FEATURE_COLUMNS[i]:30s} → {mean_abs_shap[i]:.2f}")
    except ImportError:
        print("  ⚠ SHAP not installed")


if __name__ == "__main__":
    print("[ChronoPath] Model Training Pipeline (v2)")
    print("=" * 60)

    print("\n[DATA] Generating synthetic dataset (n=5000)...")
    df = generate_synthetic_dataset(n_samples=5000)
    print(f"  Shape: {df.shape}")

    print("\n[FEATURES] Building features...")
    X, y_income, y_happiness, y_stress, groups = prepare_data(df)
    print(f"  Feature matrix: {X.shape}")
    print(f"  Features: {list(X.columns)}")

    income_model, _ = train_income_model(X, y_income, groups)
    happiness_model, _ = train_happiness_model(X, y_happiness, groups)
    stress_model, _ = train_stress_model(X, y_stress, groups)

    print("\n" + "=" * 60)
    print("SHAP EXPLAINABILITY")
    print("=" * 60)
    generate_shap_summary(income_model, X, "income")
    generate_shap_summary(happiness_model, X, "happiness")

    print("\n" + "=" * 60)
    print("✅ ALL MODELS TRAINED AND SAVED")
    print(f"   Output: {MODEL_DIR}")
    print("=" * 60)
    for f in MODEL_DIR.iterdir():
        print(f"   {f.name:40s} ({f.stat().st_size:>10,} bytes)")
