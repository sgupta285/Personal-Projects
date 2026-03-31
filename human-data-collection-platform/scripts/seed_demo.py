from __future__ import annotations

import json
from pathlib import Path

from app.services.repository import Repository


def main() -> None:
    repo = Repository()
    users = [
        {"name": "Alicia Annotator", "email": "annotator@example.com", "role": "annotator", "skill_level": "general"},
        {"name": "Riley Reviewer", "email": "reviewer@example.com", "role": "reviewer", "skill_level": "senior"},
        {"name": "Ada Admin", "email": "admin@example.com", "role": "admin", "skill_level": "ops"},
    ]
    for user in users:
        try:
            repo.create_user(user)
        except Exception:
            pass
    task_path = Path('data/sample_tasks.json')
    tasks = json.loads(task_path.read_text())
    repo.create_tasks(tasks)
    print('Seeded demo users and tasks.')


if __name__ == '__main__':
    main()
