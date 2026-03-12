from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(slots=True)
class Settings:
    root_dir: Path = Path(__file__).resolve().parents[2]
    seed: int = int(os.getenv("SEED", "42"))

    @property
    def data_dir(self) -> Path:
        return self.root_dir / "data"

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def reports_dir(self) -> Path:
        return self.root_dir / "reports"

    @property
    def dashboard_dir(self) -> Path:
        return self.root_dir / "dashboard"

    @property
    def docs_dir(self) -> Path:
        return self.root_dir / "docs"

    @property
    def database_path(self) -> Path:
        return self.data_dir / "marketing_attribution.db"

    def ensure_dirs(self) -> None:
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
