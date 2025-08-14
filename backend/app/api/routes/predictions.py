from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Optional

from ...services.prediction_service import predict_win_probability


router = APIRouter(tags=["predictions"]) 


class PredictionRequest(BaseModel):
    champions: List[str]
    lanes: List[str]
    runes: Dict[str, str]
    patch: str
    blue_side: bool


class PredictionResponse(BaseModel):
    win_probability: float
    model_version: str
    details: Optional[Dict] = None


@router.post("/predict", response_model=PredictionResponse)
async def predict(payload: PredictionRequest) -> PredictionResponse:
    probability, details = predict_win_probability(payload.model_dump())
    return PredictionResponse(
        win_probability=probability,
        model_version=details.get("model_version", "unknown"),
        details=details,
    )
