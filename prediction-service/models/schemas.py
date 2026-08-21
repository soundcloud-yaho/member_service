from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class PredictedResult(str, Enum):
    HOME = "HOME"
    DRAW = "DRAW"
    AWAY = "AWAY"


class PredictionCreate(BaseModel):
    match_id: int
    predicted_result: PredictedResult


class PredictionUpdate(BaseModel):
    predicted_result: PredictedResult


class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    match_id: int
    predicted_result: PredictedResult
    is_correct: bool | None
    created_at: datetime
    updated_at: datetime


class PredictionCount(BaseModel):
    home: int
    draw: int
    away: int


class MatchPredictionSummary(BaseModel):
    match_id: int
    total: int
    counts: PredictionCount