# backend/app/models/train_pair_model.py
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
OUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = OUT_DIR / "pair_model.joblib"

def generate_synthetic_pairs(n_samples=5000, max_grid_pos=20, seed=42):
    rng = np.random.RandomState(seed)
    X = []
    y = []
    for _ in range(n_samples):
        # choose two random qualifying positions (1..max_grid_pos)
        a = rng.randint(1, max_grid_pos + 1)
        b = rng.randint(1, max_grid_pos + 1)
        # feature: qualifying positions and their difference
        feat = [a, b, a - b]
        # outcome: finish order influenced by qualifying but with noise
        # probability A finishes ahead = logistic(-0.25*(a-b) + noise)
        score = -0.25 * (a - b) + rng.normal(scale=1.0)
        prob = 1 / (1 + np.exp(-score))
        label = 1 if rng.rand() < prob else 0
        X.append(feat)
        y.append(label)
    return np.asarray(X), np.asarray(y)

def train_and_save(n_samples=7000):
    X, y = generate_synthetic_pairs(n_samples=n_samples)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=1)
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train, y_train)
    # quick validation score
    score = clf.score(X_val, y_val)
    print("Validation accuracy:", score)
    joblib.dump(clf, MODEL_PATH)
    print("Saved model to", MODEL_PATH)

if __name__ == "__main__":
    train_and_save()
