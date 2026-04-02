from __future__ import annotations

import argparse

from mlprep.config import load_config
from mlprep.logging_utils import configure_logging
from mlprep.pipeline import PreparationPipeline
from mlprep.postgres import export_dataframe


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ML data preparation pipeline")
    parser.add_argument("command", choices=["run", "export"], nargs="?", default="run")
    args = parser.parse_args()

    cfg = load_config()
    logger = configure_logging()
    pipeline = PreparationPipeline(cfg.raw, logger)
    result = pipeline.run()

    if args.command == "export":
        prepared = result["prepared"]
        payload = prepared.X_train_transformed.assign(target=prepared.y_train)
        export_dataframe(payload, table_name=cfg.raw["postgres"]["staging_table"])
        logger.info("Exported training features to PostgreSQL")


if __name__ == "__main__":
    main()
