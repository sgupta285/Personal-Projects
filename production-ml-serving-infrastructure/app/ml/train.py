from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from uuid import uuid4

import mlflow
import numpy as np
import torch
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from app.core.config import settings
from app.ml.dataset import make_synthetic_dataset
from app.services.model_loader import ConversionModel
from app.schemas.prediction import FEATURE_ORDER


def set_seeds(seed: int = 42) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)


def train_model(epochs: int = 20, batch_size: int = 128, learning_rate: float = 1e-3) -> dict:
    set_seeds()
    dataset = make_synthetic_dataset(rows=5000, seed=42)
    train_x, test_x, train_y, test_y = train_test_split(
        dataset.features,
        dataset.labels,
        test_size=0.2,
        random_state=42,
        stratify=dataset.labels,
    )
    train_loader = DataLoader(
        TensorDataset(torch.tensor(train_x), torch.tensor(train_y).unsqueeze(-1)),
        batch_size=batch_size,
        shuffle=True,
    )

    model = ConversionModel(input_size=len(FEATURE_ORDER))
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = nn.BCEWithLogitsLoss()

    for _ in range(epochs):
        model.train()
        for batch_features, batch_labels in train_loader:
            optimizer.zero_grad()
            logits = model(batch_features)
            loss = loss_fn(logits, batch_labels)
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        test_logits = model(torch.tensor(test_x))
        test_probs = torch.sigmoid(test_logits).squeeze(-1).numpy()
        predictions = (test_probs >= 0.5).astype(int)

    accuracy = float(accuracy_score(test_y, predictions))
    ll = float(log_loss(test_y, test_probs.clip(1e-6, 1 - 1e-6)))

    artifact_dir = Path("artifacts/models")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    registry_dir = Path("artifacts/model_registry")
    registry_dir.mkdir(parents=True, exist_ok=True)
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    model_path = artifact_dir / "current_model.pt"
    torch.save(model.state_dict(), model_path)
    dataset.frame.to_csv(processed_dir / "training_snapshot.csv", index=False)

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    experiment_name = "production-ml-serving-infrastructure"
    mlflow.set_experiment(experiment_name)

    run_id = None
    with mlflow.start_run(run_name=f"conversion-model-{uuid4().hex[:8]}") as run:
        run_id = run.info.run_id
        mlflow.log_params(
            {
                "epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "feature_count": len(FEATURE_ORDER),
            }
        )
        mlflow.log_metrics({"accuracy": accuracy, "log_loss": ll})

    metadata = {
        "model_version": datetime.now(UTC).strftime("model-%Y%m%d-%H%M%S"),
        "training_run_id": run_id,
        "training_metrics": {"accuracy": round(accuracy, 6), "log_loss": round(ll, 6)},
        "trained_at": datetime.now(UTC).isoformat(),
        "feature_order": FEATURE_ORDER,
        "path": str(model_path),
    }
    (registry_dir / "current.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


if __name__ == "__main__":
    result = train_model()
    print(json.dumps(result, indent=2))
