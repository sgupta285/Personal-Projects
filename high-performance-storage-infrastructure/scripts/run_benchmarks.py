from storageinfra.benchmark import run_default_benchmarks


def main() -> None:
    raw_df, summary_df = run_default_benchmarks()
    print(raw_df.head())
    print()
    print(summary_df)


if __name__ == "__main__":
    main()
