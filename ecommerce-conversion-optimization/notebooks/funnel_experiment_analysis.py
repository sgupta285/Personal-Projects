from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
processed = ROOT / "data/processed"
artifacts = ROOT / "artifacts"

stage = pd.read_csv(processed / "funnel_stage_metrics.csv")
segment_lift = pd.read_csv(artifacts / "segment_lift_summary.csv")
summary = json.loads((artifacts / "experiment_summary.json").read_text())

print(stage)
print(summary)
print(segment_lift.head(10))
