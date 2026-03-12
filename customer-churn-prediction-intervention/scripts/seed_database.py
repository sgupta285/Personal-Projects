import pandas as pd

from churnintel.config import settings
from churnintel.storage import seed_sqlite_database


def main() -> None:
    raw_df = pd.read_csv(settings.raw_data_path)
    feature_df = pd.read_csv(settings.feature_data_path)
    seed_sqlite_database(raw_df, feature_df, settings.database_url)
    print("Database seeded.")


if __name__ == "__main__":
    main()
