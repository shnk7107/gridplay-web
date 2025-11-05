# backend/app/api/predict.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import joblib
import os
from pathlib import Path

router = APIRouter()

# model path
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "pair_model.joblib"

# simple Pydantic model for request
class PostQualReq(BaseModel):
    race_id: str
    qualifying_pos: Dict[str, int]  # e.g. {"VER": 1, "LEC": 2}

# try to load model eagerly (fallback to None if missing)
MODEL = None
if MODEL_PATH.exists():
    try:
        MODEL = joblib.load(MODEL_PATH)
        print("Loaded prediction model from", MODEL_PATH)
    except Exception as e:
        print("Failed to load model:", e)
        MODEL = None
else:
    print("Model not found at", MODEL_PATH)

@router.post("/post_qualifying")
def post_qualifying(req: PostQualReq):
    # require at least two drivers in qualifying_pos
    qp = req.qualifying_pos
    if not qp or len(qp) < 2:
        raise HTTPException(status_code=400, detail="qualifying_pos must include at least two drivers")

    # If we don't have a model, return a safe fallback (uniform-ish probabilities)
    if MODEL is None:
        # build uniform-ish probabilities based on inverse grid (lower qual pos -> higher prob)
        out = {"race_id": req.race_id, "predictions": {}}
        total_weight = 0.0
        weights = {}
        for d, pos in qp.items():
            w = 1.0 / (pos + 0.1)
            weights[d] = w
            total_weight += w
        for d, w in weights.items():
            out["predictions"][d] = {"win_prob": round(w / total_weight, 3)}
        return out

    # If model exists: compute pairwise probabilities for each pair and aggregate
    drivers = list(qp.keys())
    n = len(drivers)
    probs = {d: 0.0 for d in drivers}
    # For every pair (A,B) get probability A beats B using model
    for i in range(n):
        for j in range(i + 1, n):
            a = drivers[i]
            b = drivers[j]
            feat = [[qp[a], qp[b], qp[a] - qp[b]]]
            try:
                p = float(MODEL.predict_proba(feat)[0][1])  # probability A finishes ahead of B
            except Exception:
                p = 0.5
            # add contributions to each driver: if A beats B with prob p, then A gets +p, B gets +(1-p)
            probs[a] += p
            probs[b] += 1.0 - p

    # normalize probs to sum to 1 (average pairwise "scores")
    total = sum(probs.values())
    out = {"race_id": req.race_id, "predictions": {}}
    if total <= 0:
        for d in drivers:
            out["predictions"][d] = {"win_prob": round(1.0 / n, 3)}
    else:
        for d in drivers:
            out["predictions"][d] = {"win_prob": round(probs[d] / total, 3)}
    return out
