"""
POST /advice — AI Career Coach endpoint.

Generates personalized advice by combining:
1. User's current inputs (life decisions)
2. Model predictions (income, happiness, stress)
3. Top SHAP features (what matters most)
4. The user's specific question

Uses a structured prompt template. Falls back to rule-based advice
if no LLM API key is configured.
"""

from fastapi import APIRouter, HTTPException
import numpy as np
from app.models import AdviceRequest, AdviceResponse
from app.ml.model_loader import registry
from app.ml.feature_engineering import (
    user_input_to_feature_vector,
    FINAL_FEATURE_COLUMNS,
)
from app.core.config import settings

router = APIRouter()

# ─────────────────────────────────────────────────────
# PROMPT TEMPLATE for the LLM
# ─────────────────────────────────────────────────────

COACH_SYSTEM_PROMPT = """You are an AI Career Coach inside the "ChronoPath" app.
You give actionable, measurable, encouraging advice based on data.

RULES:
- Be specific: give numbers, timelines, and measurable steps.
- Prioritize: rank suggestions by estimated impact (highest first).
- Be honest: if the data shows trade-offs, state them.
- Stay positive: frame advice as opportunities, not criticisms.
- Keep it concise: 3-5 action items max.
- Never fabricate statistics — use the model predictions provided."""

COACH_USER_TEMPLATE = """### Current inputs
{user_inputs_summary}

### Model predictions
- Predicted income: ${predicted_income:,.0f}/year
- Predicted happiness: {predicted_happiness:.1f}/10
- Stress probability: {stress_probability:.0%}

### Top factors driving income (from model explainability)
{top_factors}

### User's question
{question}

Please respond with:
1. A direct answer to the question (2-3 sentences)
2. 3-5 prioritized action items, each with:
   - What to change
   - By how much
   - Estimated impact on income/happiness/stress"""


# ─────────────────────────────────────────────────────
# Rule-based fallback (no external API needed)
# ─────────────────────────────────────────────────────

def generate_rule_based_advice(
    inputs: dict,
    income: float,
    happiness: float,
    stress_prob: float,
    top_features: list,
    question: str,
) -> dict:
    """
    Generate advice using simple rules when no LLM API key is configured.
    """
    action_items = []

    # Analyze gaps and suggest improvements
    if inputs.get("study_hours_per_day", 0) < 2:
        action_items.append({
            "action": "Increase daily study/learning time",
            "change": f"From {inputs.get('study_hours_per_day', 0):.1f} to 2.0 hours/day",
            "impact": "Estimated +8-12% income over 3 years based on learning_rate feature",
        })

    if inputs.get("networking_hours_per_week", 0) < 3:
        action_items.append({
            "action": "Increase weekly networking",
            "change": f"From {inputs.get('networking_hours_per_week', 0):.1f} to 4 hours/week",
            "impact": "Estimated +5-8% income, +0.3 happiness points via career_score boost",
        })

    if inputs.get("exercise_days_per_week", 0) < 4:
        action_items.append({
            "action": "Exercise more frequently",
            "change": f"From {inputs.get('exercise_days_per_week', 0)} to 4-5 days/week",
            "impact": "Estimated +0.5 happiness, -10% stress probability via health_score",
        })

    if inputs.get("savings_rate_pct", 0) < 20:
        action_items.append({
            "action": "Increase savings rate",
            "change": f"From {inputs.get('savings_rate_pct', 0):.0f}% to 20%",
            "impact": "Improved financial_discipline → +5% long-term income trajectory",
        })

    if inputs.get("education_level", 0) < 4 and inputs.get("years_experience", 0) < 10:
        action_items.append({
            "action": "Consider advanced education (Master's degree or certifications)",
            "change": f"Education level {inputs.get('education_level', 0)} → 4",
            "impact": "Estimated +15-25% income based on education_level feature weight",
        })

    if inputs.get("work_hours_per_week", 40) > 50:
        action_items.append({
            "action": "Reduce work hours to improve work-life balance",
            "change": f"From {inputs.get('work_hours_per_week', 40):.0f} to 40-45 hours/week",
            "impact": "Estimated +0.8 happiness, -15% stress probability",
        })

    # Cap at 5 items
    action_items = action_items[:5]

    # Generate answer based on question keywords
    if "income" in question.lower() or "salary" in question.lower() or "earn" in question.lower():
        answer = (
            f"Based on your current profile, your predicted income is ${income:,.0f}/year. "
            f"The top factors driving your income are: {', '.join(top_features[:3])}. "
            f"Focus on the top action items below for the highest income impact."
        )
    elif "happy" in question.lower() or "happiness" in question.lower():
        answer = (
            f"Your predicted happiness score is {happiness:.1f}/10. "
            f"Exercise, work-life balance, and social connections are the biggest levers. "
            f"See the action items below for targeted improvements."
        )
    elif "stress" in question.lower():
        answer = (
            f"Your stress probability is currently {stress_prob:.0%}. "
            f"Reducing work hours and increasing exercise are the most effective interventions. "
            f"Even small changes compound over time."
        )
    else:
        answer = (
            f"Great question! Your current trajectory shows ${income:,.0f}/year income, "
            f"{happiness:.1f}/10 happiness, and {stress_prob:.0%} stress risk. "
            f"Here are the highest-impact changes you can make:"
        )

    return {
        "answer": answer,
        "action_items": action_items,
        "top_factors": top_features[:3],
    }


@router.post("", response_model=AdviceResponse)
async def get_career_advice(request: AdviceRequest):
    """
    AI Career Coach: get personalized advice based on your life decisions,
    model predictions, and the factors driving your outcomes.
    """
    if not registry.is_loaded:
        raise HTTPException(status_code=503, detail="Models not loaded.")

    inputs = request.inputs.model_dump()
    features = user_input_to_feature_vector(inputs)

    # Get predictions
    income = registry.predict_income(features)
    happiness = registry.predict_happiness(features)
    stress_prob = registry.predict_stress_probability(features)

    # Get top features from the income model
    income_model = registry.get("income")
    income_meta = registry.get_metadata("income") or {}
    feature_names = income_meta.get("features", FINAL_FEATURE_COLUMNS)

    top_features = []
    if hasattr(income_model, "feature_importances_"):
        sorted_idx = np.argsort(income_model.feature_importances_)[::-1]
        top_features = [feature_names[i] for i in sorted_idx[:5]]
    else:
        top_features = feature_names[:5]

    # Try LLM-based advice if API key is configured
    if settings.OPENAI_API_KEY:
        try:
            import openai
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            user_inputs_summary = "\n".join(
                f"- {k}: {v}" for k, v in inputs.items()
            )
            top_factors_str = "\n".join(
                f"- {f}" for f in top_features
            )

            prompt = COACH_USER_TEMPLATE.format(
                user_inputs_summary=user_inputs_summary,
                predicted_income=income,
                predicted_happiness=happiness,
                stress_probability=stress_prob,
                top_factors=top_factors_str,
                question=request.question,
            )

            response = client.chat.completions.create(
                model=settings.COACH_MODEL,
                messages=[
                    {"role": "system", "content": COACH_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=800,
            )

            llm_answer = response.choices[0].message.content

            return AdviceResponse(
                answer=llm_answer,
                action_items=[{"action": "See detailed advice above", "impact": "varies"}],
                top_factors=top_features[:3],
            )

        except Exception as e:
            # Fall through to rule-based
            print(f"LLM advice failed: {e}. Falling back to rule-based.")

    # Rule-based fallback
    result = generate_rule_based_advice(
        inputs, income, happiness, stress_prob, top_features, request.question
    )

    return AdviceResponse(**result)
