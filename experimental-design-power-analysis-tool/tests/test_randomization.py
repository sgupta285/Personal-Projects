import pandas as pd

from expower.randomization import blocked_randomization, cluster_randomization, complete_randomization


def test_complete_randomization_preserves_subject_count():
    df = complete_randomization([f"s{i}" for i in range(10)])
    assert len(df) == 10
    assert set(df["assignment"]) == {"treatment", "control"}


def test_blocked_randomization_keeps_block_column():
    subjects = pd.DataFrame(
        {
            "subject_id": ["s1", "s2", "s3", "s4"],
            "country": ["US", "US", "CA", "CA"],
        }
    )
    df = blocked_randomization(subjects, block_column="country")
    assert "country" in df.columns
    assert len(df) == 4


def test_cluster_randomization_renames_identifier():
    df = cluster_randomization(["a", "b", "c", "d"])
    assert "cluster_id" in df.columns
