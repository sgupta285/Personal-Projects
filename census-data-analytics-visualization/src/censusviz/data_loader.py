from __future__ import annotations

from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"


def load_state_metrics() -> pd.DataFrame:
    return pd.read_csv(DATA_PROCESSED / "state_metrics.csv", dtype={"fips": str})


def load_county_metrics() -> pd.DataFrame:
    return pd.read_csv(DATA_PROCESSED / "county_metrics.csv", dtype={"fips": str, "state_fips": str})


def load_geojson(name: str) -> dict:
    import json

    with open(DATA_RAW / name, "r", encoding="utf-8") as handle:
        return json.load(handle)
