from __future__ import annotations

from typing import Dict, Tuple

from ..core.config import settings


_MODEL = None
_MODEL_VERSION = "0.0.1-stub"


def _load_model_if_needed() -> None:
    global _MODEL
    if _MODEL is not None:
        return
    # TODO: Replace with real joblib load
    # from joblib import load
    # _MODEL = load(settings.model_path)
    _MODEL = "stub-model"


def predict_win_probability(features: Dict) -> Tuple[float, Dict]:
    _load_model_if_needed()
    # TODO: Replace with real feature extraction and model prediction
    # probability = float(_MODEL.predict_proba([vector])[0][1])
    # Temporary deterministic placeholder based on champions count
    champions = features.get("champions", [])
    base = 0.5
    adjustment = min(len(champions) * 0.01, 0.1)
    probability = max(0.0, min(1.0, base + (adjustment if features.get("blue_side") else -adjustment)))
    return probability, {"model_version": _MODEL_VERSION, "used_model_path": settings.model_path}
