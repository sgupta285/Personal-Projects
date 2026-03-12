import pandas as pd

from pricing_engine.config import settings
from pricing_engine.features import build_feature_table
from pricing_engine.modeling import train_model


def main() -> None:
    transactions = pd.read_csv(settings.raw_transactions_path)
    features = build_feature_table(transactions)
    train_model(features, settings.artifact_dir)
    print("Model retrained and artifacts refreshed.")


if __name__ == "__main__":
    main()
