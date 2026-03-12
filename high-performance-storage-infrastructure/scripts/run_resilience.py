from pprint import pprint

from storageinfra.resilience import run_resilience_suite


def main() -> None:
    results = run_resilience_suite()
    pprint(results)


if __name__ == "__main__":
    main()
