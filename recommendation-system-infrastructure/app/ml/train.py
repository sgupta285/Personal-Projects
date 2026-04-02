from __future__ import annotations

from pathlib import Path

try:
    import mlflow
except Exception:
    mlflow = None

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from app.core.config import settings
from app.services.feature_store import FeatureStore
from app.services.ranking import Ranker


def position_bias_weight(position: int) -> float:
    return 1.0 / np.log2(position + 2)


def train() -> None:
    settings.model_dir_path.mkdir(parents=True, exist_ok=True)
    interactions = pd.read_csv("data/raw/interactions.csv")
    items = pd.read_csv("data/raw/items.csv")
    users = pd.read_csv("data/raw/users.csv")

    user_ids = users["user_id"].tolist()
    item_ids = items["item_id"].tolist()
    Path("data/processed/user_ids.txt").write_text("\n".join(user_ids))
    Path("data/processed/item_ids.txt").write_text("\n".join(item_ids))

    latent_dim = 24
    rng = np.random.default_rng(7)
    user_embeddings = rng.normal(0, 0.15, size=(len(user_ids), latent_dim)).astype(np.float32)
    item_embeddings = rng.normal(0, 0.15, size=(len(item_ids), latent_dim)).astype(np.float32)

    user_index = {user_id: idx for idx, user_id in enumerate(user_ids)}
    item_index = {item_id: idx for idx, item_id in enumerate(item_ids)}

    for row in interactions.itertuples(index=False):
        u = user_index[row.user_id]
        i = item_index[row.item_id]
        signal = 0.65 * row.clicked + 1.35 * row.purchased + 0.1 * row.seconds_watched / 60.0
        weight = position_bias_weight(int(row.position))
        update = 0.02 * signal * weight
        user_embeddings[u] += update * item_embeddings[i]
        item_embeddings[i] += update * user_embeddings[u]

    np.save(settings.user_embeddings_path, user_embeddings)
    np.save(settings.item_embeddings_path, item_embeddings)

    store = FeatureStore()
    store.load()
    rows = []
    targets = []
    sample = interactions.sample(min(6000, len(interactions)), random_state=7)
    for row in sample.itertuples(index=False):
        features = store.join_features(
            row.user_id,
            row.item_id,
            {"hour_of_day": int(row.hour_of_day), "device_type": row.device_type},
        )
        rows.append(store.as_vector(features))
        targets.append(0.7 * row.clicked + 1.5 * row.purchased + 0.2 * position_bias_weight(int(row.position)))

    x = torch.tensor(np.stack(rows), dtype=torch.float32)
    y = torch.tensor(np.array(targets), dtype=torch.float32).unsqueeze(1)
    loader = DataLoader(TensorDataset(x, y), batch_size=64, shuffle=True)

    model = Ranker(input_dim=x.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.MSELoss()

    if mlflow is not None:
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment("recommendation-system-infrastructure")
        run_context = mlflow.start_run(run_name="ranker-train")
    else:
        class NullRun:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                return False
        run_context = NullRun()

    with run_context:
        if mlflow is not None:
            mlflow.log_params({"latent_dim": latent_dim, "batch_size": 64, "epochs": 8})
        for epoch in range(8):
            losses = []
            for batch_x, batch_y in loader:
                preds = model(batch_x)
                loss = loss_fn(preds, batch_y)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                losses.append(loss.item())
            if mlflow is not None:
                mlflow.log_metric("train_loss", float(np.mean(losses)), step=epoch)
        torch.save(model.state_dict(), settings.model_dir_path / "ranking_model.pt")


if __name__ == "__main__":
    train()
