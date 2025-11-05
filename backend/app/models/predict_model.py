import numpy as np

class PredictModel:
    def __init__(self):
        self.dummy = True

    def predict_finish_probabilities(self, qualifying_pos, conditions):
        out = {}
        for d, qpos in qualifying_pos.items():
            base = max(0.01, (1.0 / (qpos + 0.5)))
            probs = {str(p): round(base * (1/(p if p>0 else 1)), 4) for p in range(1, 21)}
            s = sum(probs.values())
            for k in probs:
                probs[k] = round(probs[k]/s, 4)
            out[d] = probs
        return out
