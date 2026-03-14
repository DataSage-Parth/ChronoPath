"""
POST /predict/trajectory — Deterministic single-path prediction.

Returns model-predicted income, happiness, stress + confidence intervals
and top feature importances.
"""

from fastapi import APIRouter, HTTPException
from app.models import UserInputs, TrajectoryResponse
from app.ml.model_loader import registry
from app.ml.feature_engineering import user_input_to_feature_vector

router = APIRouter()


@router.post("/trajectory", response_model=TrajectoryResponse)
async def predict_trajectory(inputs: UserInputs):
    """
    Predict income, happiness, and stress for the given life decisions.

    Returns a deterministic single-path prediction with confidence intervals
    derived from model cross-validation RMSE.
    """
    if not registry.is_loaded:
        raise HTTPException(status_code=503, detail="Models not loaded. Train models first.")

    # Convert user inputs to feature vector
    features = user_input_to_feature_vector(inputs.model_dump())

    # Predict all three targets
    income = registry.predict_income(features)
    happiness = registry.predict_happiness(features)
    stress_prob = registry.predict_stress_probability(features)

    # Confidence intervals from model metadata (CV RMSE)
    income_meta = registry.get_metadata("income") or {}
    income_rmse = income_meta.get("cv_rmse_mean", 10000)

    happiness_meta = registry.get_metadata("happiness") or {}
    happiness_rmse = happiness_meta.get("cv_rmse_mean", 1.0)

    # Get feature importances from XGBoost
    income_model = registry.get("income")
    feature_names = income_meta.get("features", [])
    importances = {}
    if hasattr(income_model, "feature_importances_") and feature_names:
        sorted_pairs = sorted(
            zip(feature_names, income_model.feature_importances_),
            key=lambda x: x[1],
            reverse=True,
        )
        importances = {name: round(float(imp), 4) for name, imp in sorted_pairs[:8]}

    return TrajectoryResponse(
        predicted_income=round(income, 2),
        predicted_happiness=round(max(0, min(10, happiness)), 2),
        predicted_stress_probability=round(max(0, min(1, stress_prob)), 4),
        confidence_intervals={
            "income": {
                "lower_95": round(income - 1.96 * income_rmse, 2),
                "upper_95": round(income + 1.96 * income_rmse, 2),
            },
            "happiness": {
                "lower_95": round(max(0, happiness - 1.96 * happiness_rmse), 2),
                "upper_95": round(min(10, happiness + 1.96 * happiness_rmse), 2),
            },
        },
        feature_importances=importances,
    )
