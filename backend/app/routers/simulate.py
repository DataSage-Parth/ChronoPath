"""
POST /simulate — Monte Carlo simulation endpoint.

Returns percentile distributions (5th, 25th, 50th, 75th, 95th) for
income, happiness, and stress over the requested time horizon.
"""

from fastapi import APIRouter, HTTPException
from app.models import SimulateRequest, SimulateResponse
from app.ml.model_loader import registry
from app.ml.feature_engineering import user_input_to_feature_vector
from app.ml.monte_carlo import (
    run_monte_carlo,
    simulation_to_api_response,
    SimulationConfig,
)

router = APIRouter()


@router.post("", response_model=SimulateResponse)
async def run_simulation(request: SimulateRequest):
    """
    Run Monte Carlo simulation for life trajectory predictions.

    Generates N stochastic simulations and returns percentile bands
    plus 5 sample trajectories for visualization.
    """
    if not registry.is_loaded:
        raise HTTPException(status_code=503, detail="Models not loaded. Train models first.")

    inputs = request.inputs.model_dump()
    features = user_input_to_feature_vector(inputs)

    # Get base predictions from ML models
    base_income = registry.predict_income(features)
    base_happiness = registry.predict_happiness(features)
    base_stress = registry.predict_stress_probability(features)

    # Configure Monte Carlo
    config = SimulationConfig(
        n_simulations=request.n_simulations,
        years_horizon=request.years_horizon,
        random_seed=request.random_seed,
    )

    # Run simulation
    sim_results = run_monte_carlo(
        base_income_prediction=base_income,
        base_happiness_prediction=base_happiness,
        base_stress_probability=base_stress,
        user_features=inputs,
        config=config,
    )

    # Convert to API response (strips large arrays, keeps percentiles + samples)
    return simulation_to_api_response(sim_results)
