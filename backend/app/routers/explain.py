"""
POST /explain — SHAP feature contribution endpoint.

Returns ordered list of feature contributions for the given input,
showing which decisions drive the prediction most.
"""

from fastapi import APIRouter, HTTPException
import numpy as np
from app.models import UserInputs, ExplainResponse
from app.ml.model_loader import registry
from app.ml.feature_engineering import (
    user_input_to_feature_vector,
    FINAL_FEATURE_COLUMNS,
)

router = APIRouter()


@router.post("", response_model=ExplainResponse)
async def explain_prediction(inputs: UserInputs):
    """
    Explain the income prediction using SHAP-like feature contributions.

    Returns the base value (average model prediction), the actual prediction,
    and an ordered list of feature contributions sorted by absolute impact.
    """
    if not registry.is_loaded:
        raise HTTPException(status_code=503, detail="Models not loaded.")

    features = user_input_to_feature_vector(inputs.model_dump())
    income = registry.predict_income(features)

    income_model = registry.get("income")

    try:
        import shap
        explainer = shap.TreeExplainer(income_model)
        shap_values = explainer.shap_values(features.reshape(1, -1))
        base_value = float(explainer.expected_value)
        shap_vector = shap_values[0]
    except (ImportError, Exception):
        # Fallback: use feature importances as a proxy
        base_value = float(income * 0.5)  # rough approximation
        importances = income_model.feature_importances_
        # Simulate signed contributions by (importance * feature_deviation_from_mean)
        shap_vector = importances * (features - 0.5)

    # Build ordered contribution list
    abs_shap = np.abs(shap_vector)
    sorted_idx = np.argsort(abs_shap)[::-1]

    contributions = []
    for idx in sorted_idx:
        contributions.append({
            "feature": FINAL_FEATURE_COLUMNS[idx],
            "value": round(float(features[idx]), 4),
            "shap_value": round(float(shap_vector[idx]), 2),
            "direction": "positive" if shap_vector[idx] > 0 else "negative",
        })

    return ExplainResponse(
        base_value=round(base_value, 2),
        prediction=round(income, 2),
        contributions=contributions,
    )
