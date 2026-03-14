"""
ChronoPath — FastAPI Application

Start with: uvicorn app.main:app --reload --port 8000
Docs at: http://localhost:8000/docs
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.ml.model_loader import registry
from app.routers import predict, simulate, explain, advice

logger = logging.getLogger("chronopath")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML models on startup."""
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting")
    registry.load_all()
    if registry.is_loaded:
        logger.info("Models loaded — API is ready")
    else:
        logger.warning("No models found. Run: python scripts/train_models.py")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Predict the trajectory of your life decisions using ML and Monte Carlo simulation.",
    lifespan=lifespan,
)

# CORS — allow frontend dev server + production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# Mount routers
app.include_router(predict.router, prefix="/predict", tags=["Prediction"])
app.include_router(simulate.router, prefix="/simulate", tags=["Simulation"])
app.include_router(explain.router, prefix="/explain", tags=["Explainability"])
app.include_router(advice.router, prefix="/advice", tags=["AI Career Coach"])


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "models_loaded": registry.is_loaded,
        "version": settings.APP_VERSION,
    }
