from __future__ import annotations

from typing import Any

from app.config import settings
from app.db import dumps, get_connection, init_db, loads
from app.services.assignment_engine import choose_next_task
from app.services.quality import detect_response_anomalies, score_seed_task, simple_agreement


class Repository:
    def __init__(self) -> None:
        init_db()

    def create_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO users(name, email, role, skill_level) VALUES (?, ?, ?, ?)",
                (payload["name"], payload.get("email"), payload["role"], payload.get("skill_level", "general")),
            )
            row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
            row["is_active"] = bool(row["is_active"])
            return row

    def list_users(self) -> list[dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY id ASC").fetchall()
            for row in rows:
                row["is_active"] = bool(row["is_active"])
            return rows

    def create_tasks(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        created = []
        with get_connection() as conn:
            for task in tasks:
                cur = conn.execute(
                    """
                    INSERT INTO tasks(task_type, priority, batch_name, requires_review, seed_task, payload_json, gold_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task["task_type"],
                        task.get("priority", 50),
                        task.get("batch_name"),
                        int(task.get("requires_review", True)),
                        int(task.get("seed_task", False)),
                        dumps(task["payload"]),
                        dumps(task.get("gold")) if task.get("gold") is not None else None,
                    ),
                )
                row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
                created.append(self._hydrate_task(row))
        return created

    def list_tasks(self) -> list[dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM tasks ORDER BY priority DESC, id ASC").fetchall()
            return [self._hydrate_task(r) for r in rows]

    def get_task(self, task_id: int) -> dict[str, Any] | None:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            return self._hydrate_task(row) if row else None

    def assign_next_task(self, user_id: int) -> dict[str, Any] | None:
        with get_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            if not user:
                return None
            tasks = [self._hydrate_task(r) for r in conn.execute("SELECT * FROM tasks").fetchall()]
            prior = conn.execute("SELECT task_id FROM assignments WHERE user_id = ?", (user_id,)).fetchall()
            prior_ids = {row["task_id"] for row in prior}
            selected = choose_next_task(tasks, prior_ids, user["role"])
            if not selected:
                return None
            cur = conn.execute(
                "INSERT INTO assignments(task_id, user_id, status) VALUES (?, ?, 'assigned')",
                (selected["id"], user_id),
            )
            if selected["status"] == "open" and user["role"] == "annotator":
                conn.execute("UPDATE tasks SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (selected["id"],))
            assignment = conn.execute("SELECT * FROM assignments WHERE id = ?", (cur.lastrowid,)).fetchone()
            return self._hydrate_assignment(assignment, selected)

    def submit_response(self, payload: dict[str, Any]) -> dict[str, Any]:
        with get_connection() as conn:
            assignment = conn.execute("SELECT * FROM assignments WHERE id = ?", (payload["assignment_id"],)).fetchone()
            if not assignment:
                raise ValueError("Assignment not found")
            task_row = conn.execute("SELECT * FROM tasks WHERE id = ?", (assignment["task_id"],)).fetchone()
            task = self._hydrate_task(task_row)
            response = payload["response"]
            quality_flags = {
                "anomalies": detect_response_anomalies(response, payload.get("time_spent_seconds", 0)),
                "seed_score": score_seed_task(task["payload"], response, task.get("gold")),
            }
            cur = conn.execute(
                """
                INSERT INTO responses(assignment_id, task_id, user_id, response_json, quality_flags_json, time_spent_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    assignment["id"],
                    assignment["task_id"],
                    assignment["user_id"],
                    dumps(response),
                    dumps(quality_flags),
                    payload.get("time_spent_seconds", 0),
                ),
            )
            conn.execute(
                "UPDATE assignments SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?",
                (assignment["id"],),
            )
            next_status = "pending_review" if task["requires_review"] or settings.require_review_for_all else "completed"
            conn.execute(
                "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (next_status, assignment["task_id"]),
            )
            row = conn.execute("SELECT * FROM responses WHERE id = ?", (cur.lastrowid,)).fetchone()
            return self._hydrate_response(row)

    def list_pending_responses(self) -> list[dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT responses.* FROM responses
                JOIN tasks ON tasks.id = responses.task_id
                WHERE tasks.status = 'pending_review'
                ORDER BY responses.id ASC
                """
            ).fetchall()
            return [self._hydrate_response(r) for r in rows]

    def create_review(self, payload: dict[str, Any]) -> dict[str, Any]:
        with get_connection() as conn:
            response = conn.execute("SELECT * FROM responses WHERE id = ?", (payload["response_id"],)).fetchone()
            if not response:
                raise ValueError("Response not found")
            cur = conn.execute(
                "INSERT INTO reviews(response_id, reviewer_id, decision, score, notes) VALUES (?, ?, ?, ?, ?)",
                (payload["response_id"], payload["reviewer_id"], payload["decision"], payload.get("score", 0), payload.get("notes", "")),
            )
            next_status = "completed" if payload["decision"] == "approved" else "open"
            conn.execute(
                "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (next_status, response["task_id"]),
            )
            row = conn.execute("SELECT * FROM reviews WHERE id = ?", (cur.lastrowid,)).fetchone()
            return row

    def admin_metrics(self) -> dict[str, Any]:
        with get_connection() as conn:
            statuses = {row['status']: row['count'] for row in conn.execute("SELECT status, COUNT(*) AS count FROM tasks GROUP BY status")}
            total_responses = conn.execute("SELECT COUNT(*) AS count FROM responses").fetchone()["count"]
            total_reviews = conn.execute("SELECT COUNT(*) AS count FROM reviews").fetchone()["count"]
            review_score_row = conn.execute("SELECT AVG(score) AS avg_score FROM reviews").fetchone()
            throughput_rows = conn.execute(
                """
                SELECT tasks.task_type, COUNT(responses.id) AS count
                FROM tasks LEFT JOIN responses ON responses.task_id = tasks.id
                GROUP BY tasks.task_type
                """
            ).fetchall()
            throughput = {row['task_type']: row['count'] for row in throughput_rows}
            seed_scores = []
            for row in conn.execute("SELECT quality_flags_json FROM responses").fetchall():
                flags = loads(row['quality_flags_json']) or {}
                score = (((flags.get('seed_score') or {}).get('score')))
                if score is not None:
                    seed_scores.append(score)
            classification_values = []
            for row in conn.execute(
                """
                SELECT task_id, response_json FROM responses
                JOIN tasks ON tasks.id = responses.task_id
                WHERE tasks.task_type = 'classification'
                """
            ).fetchall():
                resp = loads(row['response_json']) or {}
                classification_values.append(resp.get('label', ''))
            agreement = simple_agreement(classification_values)
            return {
                'open_tasks': statuses.get('open', 0),
                'in_progress_tasks': statuses.get('in_progress', 0),
                'pending_review_tasks': statuses.get('pending_review', 0),
                'completed_tasks': statuses.get('completed', 0),
                'total_responses': total_responses,
                'total_reviews': total_reviews,
                'seed_task_accuracy': round(sum(seed_scores) / len(seed_scores), 4) if seed_scores else 0.0,
                'average_review_score': round(review_score_row['avg_score'] or 0.0, 4),
                'throughput_by_type': throughput,
                'agreement_summary': agreement,
            }

    def _hydrate_task(self, row: dict[str, Any] | None) -> dict[str, Any] | None:
        if row is None:
            return None
        return {
            'id': row['id'],
            'task_type': row['task_type'],
            'status': row['status'],
            'priority': row['priority'],
            'batch_name': row['batch_name'],
            'requires_review': bool(row['requires_review']),
            'seed_task': bool(row['seed_task']),
            'payload': loads(row['payload_json']) or {},
            'gold': loads(row['gold_json']) if row.get('gold_json') else None,
        }

    def _hydrate_assignment(self, row: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
        return {
            'id': row['id'],
            'task_id': row['task_id'],
            'user_id': row['user_id'],
            'status': row['status'],
            'task': task,
        }

    def _hydrate_response(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            'id': row['id'],
            'assignment_id': row['assignment_id'],
            'task_id': row['task_id'],
            'user_id': row['user_id'],
            'response': loads(row['response_json']) or {},
            'quality_flags': loads(row['quality_flags_json']) if row.get('quality_flags_json') else None,
            'time_spent_seconds': row['time_spent_seconds'],
        }
