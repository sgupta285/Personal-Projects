from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


def complete_randomization(subject_ids: Iterable[str], treatment_ratio: float = 1.0, seed: int = 42) -> pd.DataFrame:
    subject_ids = list(subject_ids)
    if not subject_ids:
        raise ValueError("subject_ids cannot be empty")
    rng = np.random.default_rng(seed)
    shuffled = subject_ids.copy()
    rng.shuffle(shuffled)
    treatment_share = treatment_ratio / (1 + treatment_ratio)
    treatment_n = round(len(shuffled) * treatment_share)
    assignments = ["treatment"] * treatment_n + ["control"] * (len(shuffled) - treatment_n)
    return pd.DataFrame({"subject_id": shuffled, "assignment": assignments}).sort_values("subject_id").reset_index(drop=True)


def blocked_randomization(
    subjects: pd.DataFrame,
    block_column: str,
    treatment_ratio: float = 1.0,
    seed: int = 42,
) -> pd.DataFrame:
    if block_column not in subjects.columns:
        raise KeyError(f"{block_column} not found in subjects DataFrame")

    frames = []
    for idx, (_, block_df) in enumerate(subjects.groupby(block_column, sort=True)):
        randomized = complete_randomization(
            subject_ids=block_df["subject_id"].tolist(),
            treatment_ratio=treatment_ratio,
            seed=seed + idx,
        )
        merged = randomized.merge(block_df, on="subject_id", how="left")
        frames.append(merged)
    return pd.concat(frames, ignore_index=True).sort_values(["subject_id"]).reset_index(drop=True)


def cluster_randomization(cluster_ids: Iterable[str], treatment_ratio: float = 1.0, seed: int = 42) -> pd.DataFrame:
    clusters = list(cluster_ids)
    randomized = complete_randomization(clusters, treatment_ratio=treatment_ratio, seed=seed)
    return randomized.rename(columns={"subject_id": "cluster_id"})
