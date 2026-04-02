import pandas as pd

from mlprep.config import load_config
from mlprep.feature_engineering import FeatureEngineer
from mlprep.preprocessing import Preprocessor


def test_preprocessor_preserves_train_test_separation() -> None:
    cfg = load_config().raw
    df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4, 5, 6],
            "monthly_spend": [10, 20, 30, 4000, 25, 15],
            "sessions_last_30d": [1, 5, 10, 3, 8, 12],
            "avg_session_minutes": [5, 7, 6, 8, 7, 9],
            "support_tickets": [1, 0, 1, 4, 0, 1],
            "account_age_days": [50, 60, 70, 80, 90, 100],
            "region": ["west", "south", "west", "midwest", "south", "west"],
            "device_type": ["web", "ios", "android", "web", "ios", "android"],
            "plan_tier": ["basic", "pro", "pro", "business", "basic", "pro"],
            "signup_channel": ["organic", "paid", "organic", "partner", "sales", "organic"],
            "is_premium": [0, 1, 1, 1, 0, 1],
            "churned": [0, 1, 0, 1, 0, 1],
        }
    )
    engineered = FeatureEngineer(cfg).transform(df)
    prepared = Preprocessor(cfg).prepare(engineered, "churned")
    assert len(prepared.X_train_raw) + len(prepared.X_test_raw) == len(df)
    assert set(prepared.X_train_raw.index).isdisjoint(set(prepared.X_test_raw.index))
    assert prepared.X_train_transformed.shape[1] == prepared.X_test_transformed.shape[1]
