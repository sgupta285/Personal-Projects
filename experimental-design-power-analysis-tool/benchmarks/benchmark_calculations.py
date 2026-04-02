from __future__ import annotations

import time
from statistics import mean

from expower.power import ClusteredDesignInputs, PairedDesignInputs, TwoSampleDesignInputs, recommend_clustered_design, recommend_paired_design, recommend_two_sample_design


def time_call(fn, repeats: int = 200) -> float:
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return mean(samples)


def main() -> None:
    between = time_call(lambda: recommend_two_sample_design(TwoSampleDesignInputs()))
    paired = time_call(lambda: recommend_paired_design(PairedDesignInputs()))
    clustered = time_call(lambda: recommend_clustered_design(ClusteredDesignInputs()))
    print("average_runtime_seconds")
    print(f"between_subjects,{between:.6f}")
    print(f"within_subjects,{paired:.6f}")
    print(f"clustered,{clustered:.6f}")


if __name__ == "__main__":
    main()
