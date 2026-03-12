from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Settings:
    root_dir: Path = Path(__file__).resolve().parents[2]

    @property
    def random_seed(self) -> int:
        return int(os.getenv("RANDOM_SEED", "42"))

    @property
    def database_url(self) -> str:
        return os.getenv("DATABASE_URL", "sqlite:///./data/ecommerce.db")

    @property
    def raw_events_path(self) -> Path:
        return self.root_dir / os.getenv("RAW_EVENTS_PATH", "data/raw/events.csv")

    @property
    def raw_sessions_path(self) -> Path:
        return self.root_dir / os.getenv("RAW_SESSIONS_PATH", "data/raw/sessions.csv")

    @property
    def stage_metrics_path(self) -> Path:
        return self.root_dir / os.getenv("STAGE_METRICS_PATH", "data/processed/funnel_stage_metrics.csv")

    @property
    def segment_metrics_path(self) -> Path:
        return self.root_dir / os.getenv("SEGMENT_METRICS_PATH", "data/processed/funnel_segment_metrics.csv")

    @property
    def experiment_cohorts_path(self) -> Path:
        return self.root_dir / os.getenv("EXPERIMENT_COHORTS_PATH", "data/processed/experiment_cohorts.csv")

    @property
    def artifact_dir(self) -> Path:
        return self.root_dir / os.getenv("ARTIFACT_DIR", "artifacts")

    def ensure_directories(self) -> None:
        self.raw_events_path.parent.mkdir(parents=True, exist_ok=True)
        self.raw_sessions_path.parent.mkdir(parents=True, exist_ok=True)
        self.stage_metrics_path.parent.mkdir(parents=True, exist_ok=True)
        self.segment_metrics_path.parent.mkdir(parents=True, exist_ok=True)
        self.experiment_cohorts_path.parent.mkdir(parents=True, exist_ok=True)
        (self.artifact_dir / "figures").mkdir(parents=True, exist_ok=True)


settings = Settings()
