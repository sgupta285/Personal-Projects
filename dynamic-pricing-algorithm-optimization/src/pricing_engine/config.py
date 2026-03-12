from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Settings:
    root_dir: Path = Path(__file__).resolve().parents[2]
    random_seed: int = 42

    @property
    def artifact_dir(self) -> Path:
        return self.root_dir / os.getenv("ARTIFACT_DIR", "artifacts")

    @property
    def raw_transactions_path(self) -> Path:
        return self.root_dir / os.getenv("RAW_TRANSACTIONS_PATH", "data/raw/transactions.csv")

    @property
    def raw_catalog_path(self) -> Path:
        return self.root_dir / os.getenv("RAW_CATALOG_PATH", "data/raw/product_catalog.csv")

    @property
    def processed_feature_path(self) -> Path:
        return self.root_dir / os.getenv("PROCESSED_FEATURE_PATH", "data/processed/pricing_features.csv")

    @property
    def database_path(self) -> Path:
        return self.root_dir / os.getenv("DATABASE_PATH", "data/pricing.db")

    @property
    def objective(self) -> str:
        return os.getenv("OBJECTIVE", "gross_profit")

    def ensure_directories(self) -> None:
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.raw_transactions_path.parent.mkdir(parents=True, exist_ok=True)
        self.raw_catalog_path.parent.mkdir(parents=True, exist_ok=True)
        self.processed_feature_path.parent.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
