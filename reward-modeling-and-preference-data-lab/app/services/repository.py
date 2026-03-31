from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from app.db import dumps, get_connection, init_db


class PreferenceLabRepository:
    def __init__(self) -> None:
        init_db()

    def create_dataset(self, name: str, description: str, task_family: str) -> dict[str, Any]:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO datasets(name, description, task_family) VALUES (?, ?, ?)",
                (name, description, task_family),
            )
            dataset_id = cur.lastrowid
        return self.get_dataset(dataset_id)

    def list_datasets(self) -> list[dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM datasets ORDER BY id").fetchall()
            return [dict(row) for row in rows]

    def get_dataset(self, dataset_id: int) -> dict[str, Any]:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,)).fetchone()
            if row is None:
                raise KeyError(f"Dataset {dataset_id} not found")
            return dict(row)

    def create_example(
        self,
        dataset_id: int,
        prompt_text: str,
        task_type: str,
        context: dict[str, Any],
        metadata: dict[str, Any],
        candidates: list[dict[str, Any]],
    ) -> dict[str, Any]:
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO preference_examples(dataset_id, prompt_text, task_type, context_json, metadata_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (dataset_id, prompt_text, task_type, dumps(context), dumps(metadata)),
            )
            example_id = cur.lastrowid
            for candidate in candidates:
                conn.execute(
                    """
                    INSERT INTO candidates(example_id, label, response_text, model_name, metadata_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        example_id,
                        candidate["label"],
                        candidate["response_text"],
                        candidate.get("model_name"),
                        dumps(candidate.get("metadata", {})),
                    ),
                )
        return self.get_example(example_id)

    def list_examples(self, dataset_id: int | None = None) -> list[dict[str, Any]]:
        query = "SELECT id FROM preference_examples"
        params: tuple[Any, ...] = ()
        if dataset_id is not None:
            query += " WHERE dataset_id = ?"
            params = (dataset_id,)
        query += " ORDER BY id"
        with get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self.get_example(row["id"]) for row in rows]

    def get_example(self, example_id: int) -> dict[str, Any]:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM preference_examples WHERE id = ?", (example_id,)).fetchone()
            if row is None:
                raise KeyError(f"Example {example_id} not found")
            example = dict(row)
            example["context"] = json.loads(example.pop("context_json"))
            example["metadata"] = json.loads(example.pop("metadata_json"))
            candidates = conn.execute(
                "SELECT * FROM candidates WHERE example_id = ? ORDER BY id",
                (example_id,),
            ).fetchall()
            example["candidates"] = [
                {
                    **dict(candidate),
                    "metadata": json.loads(candidate["metadata_json"]),
                }
                for candidate in candidates
            ]
            for candidate in example["candidates"]:
                candidate.pop("metadata_json", None)
            return example

    def submit_preference(
        self,
        example_id: int,
        annotator_id: str,
        ranking: list[int],
        notes: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        winner = ranking[0] if ranking else None
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO preferences(example_id, annotator_id, winner_candidate_id, ranking_json, notes, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (example_id, annotator_id, winner, dumps(ranking), notes, dumps(metadata)),
            )
            preference_id = cur.lastrowid
        return self.get_preference(preference_id)

    def list_preferences(self, dataset_id: int | None = None) -> list[dict[str, Any]]:
        with get_connection() as conn:
            if dataset_id is None:
                rows = conn.execute("SELECT id FROM preferences ORDER BY id").fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT p.id
                    FROM preferences p
                    JOIN preference_examples e ON e.id = p.example_id
                    WHERE e.dataset_id = ?
                    ORDER BY p.id
                    """,
                    (dataset_id,),
                ).fetchall()
        return [self.get_preference(row["id"]) for row in rows]

    def get_preference(self, preference_id: int) -> dict[str, Any]:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM preferences WHERE id = ?", (preference_id,)).fetchone()
            if row is None:
                raise KeyError(f"Preference {preference_id} not found")
            preference = dict(row)
            preference["ranking"] = json.loads(preference.pop("ranking_json"))
            preference["metadata"] = json.loads(preference.pop("metadata_json"))
            return preference

    def upsert_reward_target(self, example_id: int, method: str, targets: dict[str, float]) -> dict[str, Any]:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO reward_targets(example_id, targets_json, method)
                VALUES (?, ?, ?)
                ON CONFLICT(example_id) DO UPDATE SET targets_json = excluded.targets_json, method = excluded.method
                """,
                (example_id, dumps(targets), method),
            )
            row = conn.execute("SELECT * FROM reward_targets WHERE example_id = ?", (example_id,)).fetchone()
            target = dict(row)
            target["targets"] = json.loads(target.pop("targets_json"))
            return target

    def get_reward_target(self, example_id: int) -> dict[str, Any]:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM reward_targets WHERE example_id = ?", (example_id,)).fetchone()
            if row is None:
                raise KeyError(f"Reward target for example {example_id} not found")
            target = dict(row)
            target["targets"] = json.loads(target.pop("targets_json"))
            return target

    def create_snapshot(self, dataset_id: int, version_name: str, manifest: dict[str, Any]) -> dict[str, Any]:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO dataset_snapshots(dataset_id, version_name, manifest_json) VALUES (?, ?, ?)",
                (dataset_id, version_name, dumps(manifest)),
            )
            snapshot_id = cur.lastrowid
        return self.get_snapshot(snapshot_id)

    def list_snapshots(self, dataset_id: int | None = None) -> list[dict[str, Any]]:
        with get_connection() as conn:
            if dataset_id is None:
                rows = conn.execute("SELECT id FROM dataset_snapshots ORDER BY id").fetchall()
            else:
                rows = conn.execute(
                    "SELECT id FROM dataset_snapshots WHERE dataset_id = ? ORDER BY id",
                    (dataset_id,),
                ).fetchall()
        return [self.get_snapshot(row["id"]) for row in rows]

    def get_snapshot(self, snapshot_id: int) -> dict[str, Any]:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM dataset_snapshots WHERE id = ?", (snapshot_id,)).fetchone()
            if row is None:
                raise KeyError(f"Snapshot {snapshot_id} not found")
            snapshot = dict(row)
            snapshot["manifest"] = json.loads(snapshot.pop("manifest_json"))
            return snapshot

    def create_experiment_run(self, dataset_id: int, snapshot_id: int | None, name: str, config: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO experiment_runs(dataset_id, snapshot_id, name, config_json, metrics_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (dataset_id, snapshot_id, name, dumps(config), dumps(metrics)),
            )
            experiment_id = cur.lastrowid
        return self.get_experiment_run(experiment_id)

    def list_experiment_runs(self, dataset_id: int | None = None) -> list[dict[str, Any]]:
        with get_connection() as conn:
            if dataset_id is None:
                rows = conn.execute("SELECT id FROM experiment_runs ORDER BY id").fetchall()
            else:
                rows = conn.execute(
                    "SELECT id FROM experiment_runs WHERE dataset_id = ? ORDER BY id",
                    (dataset_id,),
                ).fetchall()
        return [self.get_experiment_run(row["id"]) for row in rows]

    def get_experiment_run(self, experiment_id: int) -> dict[str, Any]:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM experiment_runs WHERE id = ?", (experiment_id,)).fetchone()
            if row is None:
                raise KeyError(f"Experiment run {experiment_id} not found")
            run = dict(row)
            run["config"] = json.loads(run.pop("config_json"))
            run["metrics"] = json.loads(run.pop("metrics_json"))
            return run

    def overview_counts(self) -> dict[str, Any]:
        with get_connection() as conn:
            datasets = conn.execute("SELECT COUNT(*) AS count FROM datasets").fetchone()["count"]
            examples = conn.execute("SELECT COUNT(*) AS count FROM preference_examples").fetchone()["count"]
            preferences = conn.execute("SELECT COUNT(*) AS count FROM preferences").fetchone()["count"]
            snapshots = conn.execute("SELECT COUNT(*) AS count FROM dataset_snapshots").fetchone()["count"]
            experiments = conn.execute("SELECT COUNT(*) AS count FROM experiment_runs").fetchone()["count"]
            task_rows = conn.execute(
                "SELECT task_type, COUNT(*) AS count FROM preference_examples GROUP BY task_type ORDER BY task_type"
            ).fetchall()
            annotator_rows = conn.execute(
                "SELECT annotator_id, COUNT(*) AS count FROM preferences GROUP BY annotator_id ORDER BY annotator_id"
            ).fetchall()
        return {
            "datasets": datasets,
            "examples": examples,
            "preferences": preferences,
            "snapshots": snapshots,
            "experiments": experiments,
            "examples_per_task_type": {row["task_type"]: row["count"] for row in task_rows},
            "preferences_per_annotator": {row["annotator_id"]: row["count"] for row in annotator_rows},
        }

    def preferences_grouped_by_example(self, dataset_id: int) -> dict[int, list[dict[str, Any]]]:
        grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for preference in self.list_preferences(dataset_id=dataset_id):
            grouped[preference["example_id"]].append(preference)
        return grouped
