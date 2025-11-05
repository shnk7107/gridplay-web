from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
import random

router = APIRouter()

class BattleSubmission(BaseModel):
    user_id: str
    race_id: str
    prediction: Dict[str,int]

LEADERBOARD = []

@router.post("/submit")
def submit_battle(sub: BattleSubmission):
    score = random.randint(0, 100)
    LEADERBOARD.append({"user_id": sub.user_id, "race_id": sub.race_id, "score": score})
    return {"score": score, "leaderboard_top": sorted(LEADERBOARD, key=lambda x: -x["score"])[:10]}
