from pathlib import Path

import joblib

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "ad_risk_model.joblib"


class KeywordFallbackModel:
    def predict_proba(self, texts: list[str]):
        scores = []
        for text in texts:
            lowered = text.lower()
            suspicious = sum(
                token in lowered
                for token in [
                    "guaranteed",
                    "crypto",
                    "miracle",
                    "instant approval",
                    "click now",
                    "earn $",
                    "free money",
                ]
            )
            probability = min(0.15 + suspicious * 0.15, 0.95)
            scores.append([1 - probability, probability])
        return scores


def build_classifier_input(payload: dict) -> str:
    fields = [
        payload.get("title", ""),
        payload.get("body", ""),
        payload.get("call_to_action", ""),
        payload.get("creative_text", ""),
        payload.get("category", ""),
        payload.get("landing_page_url", ""),
        " ".join(payload.get("creative_tags", []) or []),
    ]
    return " ".join(str(item) for item in fields if item)


def load_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return KeywordFallbackModel()


def score_payload(payload: dict) -> float:
    model = load_model()
    text = build_classifier_input(payload)
    probability = model.predict_proba([text])[0][1]
    return round(float(probability), 4)
