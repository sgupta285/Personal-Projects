from expower.analysis_plan import recommend_analysis_plan
from expower.power import ClusteredDesignInputs, PairedDesignInputs, TwoSampleDesignInputs, recommend_clustered_design, recommend_paired_design, recommend_two_sample_design
from expower.randomization import blocked_randomization
import pandas as pd


def main() -> None:
    between = recommend_two_sample_design(TwoSampleDesignInputs())
    paired = recommend_paired_design(PairedDesignInputs())
    clustered = recommend_clustered_design(ClusteredDesignInputs())
    subjects = pd.DataFrame(
        {
            "subject_id": [f"s{i}" for i in range(8)],
            "country": ["US", "US", "US", "US", "CA", "CA", "CA", "CA"],
        }
    )
    randomized = blocked_randomization(subjects, block_column="country")
    plan = recommend_analysis_plan("between_subjects", "continuous")
    assert between.total_required_n > 0
    assert paired.total_required_n > 0
    assert clustered.total_required_n >= between.total_required_n
    assert len(randomized) == len(subjects)
    assert "Average treatment effect" in plan.estimand
    print("smoke test passed")


if __name__ == "__main__":
    main()
