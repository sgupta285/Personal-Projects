from churnintel.config import settings
from churnintel.data_generation import generate_dataset, save_raw_dataset
from churnintel.features import build_feature_table, save_feature_table
from churnintel.modeling import train_and_export
from churnintel.storage import seed_sqlite_database
from churnintel.visuals import generate_preview_images


def main() -> None:
    settings.ensure_directories()

    raw_df = generate_dataset(n_customers=3500, seed=settings.random_seed)
    save_raw_dataset(raw_df, settings.raw_data_path)

    feature_df = build_feature_table(raw_df)
    save_feature_table(feature_df, settings.feature_data_path)

    seed_sqlite_database(raw_df, feature_df, settings.database_url)
    train_and_export(feature_df, settings.artifact_dir)
    generate_preview_images()

    print(f"Bootstrap complete. Artifacts written to {settings.artifact_dir}")


if __name__ == "__main__":
    main()
