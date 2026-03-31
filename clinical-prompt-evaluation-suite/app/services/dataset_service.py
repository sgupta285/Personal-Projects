from __future__ import annotations

import csv
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app import models
from app.schemas import DatasetCreate


def create_dataset(db: Session, payload: DatasetCreate) -> models.Dataset:
    dataset = models.Dataset(
        name=payload.name,
        workflow_name=payload.workflow_name,
        description=payload.description,
    )
    db.add(dataset)
    db.flush()
    for item in payload.items:
        db.add(
            models.DatasetItem(
                dataset_id=dataset.id,
                item_key=item.item_key,
                input_text=item.input_text,
                expected_output=item.expected_output,
                expected_keywords=item.expected_keywords,
                difficulty=item.difficulty,
                split=item.split,
            )
        )
    db.commit()
    db.refresh(dataset)
    return dataset


def import_dataset_from_json(db: Session, path: str | Path) -> models.Dataset:
    payload = DatasetCreate(**json.loads(Path(path).read_text(encoding="utf-8")))
    return create_dataset(db, payload)


def import_dataset_from_csv(
    db: Session,
    path: str | Path,
    *,
    name: str,
    workflow_name: str,
    description: str | None = None,
):
    items = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            items.append(
                {
                    "item_key": row["item_key"],
                    "input_text": row["input_text"],
                    "expected_output": json.loads(row["expected_output"]),
                    "expected_keywords": json.loads(row["expected_keywords"]),
                    "difficulty": row.get("difficulty", "medium"),
                    "split": row.get("split", "test"),
                }
            )
    payload = DatasetCreate(name=name, workflow_name=workflow_name, description=description, items=items)
    return create_dataset(db, payload)
