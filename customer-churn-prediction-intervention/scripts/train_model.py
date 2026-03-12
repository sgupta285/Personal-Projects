import pandas as pd

from churnintel.config import settings
from churnintel.features import build_feature_table
from churnintel.modeling import train_and_export
from churnintel.visuals import generate_preview_images


def main() -> None:
    settings.ensure_directories()

    if settings.raw_data_path.exists():
        raw_df = pd.read_csv(settings.raw_data_path)
    else:
        raise FileNotFoundError(
            f"Raw data not found at {settings.raw_data_path}. Run scripts/bootstrap.py first."
        )

    feature_df = build_feature_table(raw_df)
    train_and_export(feature_df, settings.artifact_dir)
    generate_preview_images()
    print("Model artifacts refreshed.")


if __name__ == "__main__":
    main()
