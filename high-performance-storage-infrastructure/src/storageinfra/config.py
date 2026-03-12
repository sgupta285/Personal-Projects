from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Settings:
    root_dir: Path = Path(__file__).resolve().parents[2]

    @property
    def storage_mode(self) -> str:
        return os.getenv("STORAGE_MODE", "local").lower()

    @property
    def cache_mode(self) -> str:
        return os.getenv("CACHE_MODE", "memory").lower()

    @property
    def bucket(self) -> str:
        return os.getenv("OBJECT_BUCKET", "benchmarks")

    @property
    def store_root(self) -> Path:
        return self.root_dir / os.getenv("STORE_ROOT", "data/store")

    @property
    def benchmark_dir(self) -> Path:
        return self.root_dir / os.getenv("BENCHMARK_OUTPUT_DIR", "data/benchmarks")

    @property
    def report_dir(self) -> Path:
        return self.root_dir / os.getenv("REPORT_OUTPUT_DIR", "data/reports")

    @property
    def hot_object_count(self) -> int:
        return int(os.getenv("HOT_OBJECT_COUNT", "8"))

    @property
    def seed(self) -> int:
        return int(os.getenv("RUN_SEED", "42"))

    @property
    def minio_endpoint(self) -> str:
        return os.getenv("MINIO_ENDPOINT", "http://localhost:9000")

    @property
    def minio_access_key(self) -> str:
        return os.getenv("MINIO_ACCESS_KEY", "minioadmin")

    @property
    def minio_secret_key(self) -> str:
        return os.getenv("MINIO_SECRET_KEY", "minioadmin")

    @property
    def minio_secure(self) -> bool:
        return os.getenv("MINIO_SECURE", "false").lower() == "true"

    @property
    def cache_capacity_bytes(self) -> int:
        return int(float(os.getenv("CACHE_CAPACITY_MB", "64")) * 1024 * 1024)

    @property
    def scenario_config_path(self) -> Path:
        return self.root_dir / "config/benchmark_scenarios.json"

    def load_scenarios(self) -> dict:
        return json.loads(self.scenario_config_path.read_text())

    def ensure_directories(self) -> None:
        self.store_root.mkdir(parents=True, exist_ok=True)
        self.benchmark_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
