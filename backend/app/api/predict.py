from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from app.models.predict_model import PredictModel

router = APIRouter()
model = PredictModel()

class PredictRequest(BaseModel):
    race_id: str
    qualifying_pos: Dict[str, int]
    conditions: Dict[str, Any] = {}

@router.post("/post_qualifying")
def post_qualifying_predict(req: PredictRequest):
    preds = model.predict_finish_probabilities(req.qualifying_pos, req.conditions)
    return {"race_id": req.race_id, "predictions": preds}
