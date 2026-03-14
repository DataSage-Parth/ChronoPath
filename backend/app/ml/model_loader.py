"""
Model loader — loads saved .joblib models and metadata.
"""

import logging
import joblib
import json
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("chronopath.models")

MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "models"


class ModelRegistry:
    """Thread-safe singleton registry for loaded ML models."""

    _instance = None
    _models: Dict[str, Any] = {}
    _metadata: Dict[str, Dict] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._models = {}
            cls._metadata = {}
        return cls._instance

    def load_all(self):
        """Load all models from the models directory."""
        model_files = {
            "income": "income_xgboost.joblib",
            "happiness": "happiness_gbr.joblib",
            "stress": "stress_calibrated_lr.joblib",
        }

        for name, filename in model_files.items():
            path = MODEL_DIR / filename
            if path.exists():
                self._models[name] = joblib.load(path)
                logger.info(f"Loaded {name} model from {path.name}")

                meta_path = MODEL_DIR / f"{name}_metadata.json"
                if meta_path.exists():
                    with open(meta_path) as f:
                        self._metadata[name] = json.load(f)
            else:
                logger.warning(f"Model not found: {path}")

    def get(self, name: str) -> Optional[Any]:
        """Get a loaded model by name."""
        return self._models.get(name)

    def get_metadata(self, name: str) -> Optional[Dict]:
        """Get model metadata by name."""
        return self._metadata.get(name)

    def predict_income(self, features) -> float:
        """Predict annual income from feature vector."""
        model = self.get("income")
        if model is None:
            raise RuntimeError("Income model not loaded. Run train_models.py first.")
        return float(model.predict(features.reshape(1, -1))[0])

    def predict_happiness(self, features) -> float:
        """Predict happiness score (0-10) from feature vector."""
        model = self.get("happiness")
        if model is None:
            raise RuntimeError("Happiness model not loaded.")
        return float(model.predict(features.reshape(1, -1))[0])

    def predict_stress_probability(self, features) -> float:
        """Predict probability of high stress from feature vector."""
        model = self.get("stress")
        if model is None:
            raise RuntimeError("Stress model not loaded.")
        return float(model.predict_proba(features.reshape(1, -1))[0, 1])

    @property
    def is_loaded(self) -> bool:
        return len(self._models) > 0


# Global singleton
registry = ModelRegistry()
