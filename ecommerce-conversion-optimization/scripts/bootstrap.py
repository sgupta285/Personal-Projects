from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ecomopt.config import settings
from ecomopt.data_generation import generate_sessions, expand_events, save_raw_data
from ecomopt.reporting import build_reports
from ecomopt.warehouse import export_sql_models, seed_database


def main() -> None:
    settings.ensure_directories()
    sessions = generate_sessions(n_sessions=24000, seed=settings.random_seed)
    events = expand_events(sessions)
    save_raw_data(sessions, events, settings.raw_sessions_path, settings.raw_events_path)
    seed_database(settings.database_url, sessions, events)
    outputs = export_sql_models(settings.database_url)
    build_reports(outputs, settings.artifact_dir)
    print(f"Bootstrap complete. Artifacts written to {settings.artifact_dir}")


if __name__ == "__main__":
    main()
