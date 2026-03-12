from storageinfra.benchmark import run_default_benchmarks
from storageinfra.reporting import write_reports
from storageinfra.resilience import run_resilience_suite


def main() -> None:
    raw_df, summary_df = run_default_benchmarks()
    resilience = run_resilience_suite()
    write_reports(raw_df, summary_df, resilience)
    print("Bootstrap complete. Benchmark and report artifacts are available in data/.")


if __name__ == "__main__":
    main()
