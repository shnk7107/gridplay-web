# backend/app/api/battles.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
import json

from ..db import SessionLocal, init_db
from ..models_db import Battle

router = APIRouter()

# Ensure DB initialized on import
init_db()

# Pydantic model for incoming submission
class BattleSubmitReq(BaseModel):
    user_id: str
    race_id: str
    prediction: Dict[str, int]  # mapping driver -> finishing position (or position guess)

def compute_score(prediction: Dict[str, int]) -> int:
    """
    Simple deterministic scoring:
    - lower predicted position (closer to 1) yields higher score,
    - reward compact correctness: sum of (max_pos + 1 - pos).
    This is intentionally simple; replace with real scoring later.
    """
    if not prediction:
        return 0
    # treat missing/invalid as worst (pos = 50)
    score = 0
    for driver, pos in prediction.items():
        try:
            p = int(pos)
        except Exception:
            p = 50
        # simple: higher points for better predicted position
        score += max(0, 25 - p)  # driver predicted 1 => 24 pts, predicted 24 => 1 pt
    return int(score)

# Dependency to provide DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/submit")
def submit_battle(req: BattleSubmitReq, db=Depends(get_db)):
    if not req.user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    # compute score
    score = compute_score(req.prediction)

    # Save to DB
    battle = Battle(
        user_id=req.user_id,
        race_id=req.race_id,
        prediction_json=json.dumps(req.prediction),
        score=score
    )
    db.add(battle)
    db.commit()
    db.refresh(battle)

    # Return the saved record and top leaderboard
    leaderboard = (
        db.query(Battle.user_id, Battle.race_id, Battle.score)
        .filter(Battle.race_id == req.race_id)
        .order_by(Battle.score.desc(), Battle.created_at.asc())
        .limit(10)
        .all()
    )
    top = [{"user_id": r[0], "race_id": r[1], "score": r[2]} for r in leaderboard]

    return JSONResponse(content={"id": battle.id, "score": battle.score, "leaderboard_top": top})

@router.get("/leaderboard/{race_id}")
def get_leaderboard(race_id: str, db=Depends(get_db)):
    rows = (
        db.query(Battle.user_id, Battle.score, Battle.created_at)
        .filter(Battle.race_id == race_id)
        .order_by(Battle.score.desc(), Battle.created_at.asc())
        .limit(50)
        .all()
    )
    out = [{"user_id": r[0], "score": r[1], "created_at": r[2].isoformat()} for r in rows]
    return JSONResponse(content={"race_id": race_id, "leaderboard": out})
