from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "backend" / "worker" / "data" / "training_ads.csv"
MODEL_PATH = ROOT / "backend" / "worker" / "artifacts" / "ad_risk_model.joblib"


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ("clf", LogisticRegression(max_iter=500, class_weight="balanced")),
        ]
    )
    pipeline.fit(df["text"], df["label"])
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Saved model artifact to {MODEL_PATH}")


if __name__ == "__main__":
    main()
