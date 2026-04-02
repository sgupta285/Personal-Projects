from __future__ import annotations

import json
from pathlib import Path

from .analysis_plan import recommend_analysis_plan
from .power import ClusteredDesignInputs, PairedDesignInputs, TwoSampleDesignInputs, cost_curve, recommend_clustered_design, recommend_paired_design, recommend_two_sample_design


def main() -> None:
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    reports = {
        "between_subjects": recommend_two_sample_design(TwoSampleDesignInputs()).to_dict(),
        "within_subjects": recommend_paired_design(PairedDesignInputs()).to_dict(),
        "clustered": recommend_clustered_design(ClusteredDesignInputs()).to_dict(),
        "analysis_plan": recommend_analysis_plan("between_subjects", "continuous").to_dict(),
        "cost_curve": cost_curve(max_budget=2000, design="between", effect_size=0.3),
    }

    output_path = artifacts_dir / "demo_report.json"
    output_path.write_text(json.dumps(reports, indent=2))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
