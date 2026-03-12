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
    def raw_data_path(self) -> Path:
        return self.root_dir / os.getenv("RAW_DATA_PATH", "data/raw/customer_events.csv")

    @property
    def feature_data_path(self) -> Path:
        return self.root_dir / os.getenv("FEATURE_DATA_PATH", "data/processed/customer_features.csv")

    @property
    def screenshots_dir(self) -> Path:
        return self.root_dir / "docs" / "screenshots"

    @property
    def database_url(self) -> str:
        return os.getenv("DATABASE_URL", "sqlite:///./data/churn.db")

    @property
    def churn_label_window_days(self) -> int:
        return int(os.getenv("CHURN_LABEL_WINDOW_DAYS", "60"))

    def ensure_directories(self) -> None:
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.raw_data_path.parent.mkdir(parents=True, exist_ok=True)
        self.feature_data_path.parent.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
