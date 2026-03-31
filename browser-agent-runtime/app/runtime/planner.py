from __future__ import annotations

from app.schemas import PlannedAction


class RuleBasedPlanner:
    '''
    A deterministic planner that turns simple task definitions into executable actions.

    This is intentionally straightforward so the runtime remains easy to test and reason about.
    In a later version, the same interface can be backed by a model without changing executor code.
    '''

    def build_plan(self, instruction: str, start_url: str | None = None) -> list[PlannedAction]:
        actions: list[PlannedAction] = []

        if start_url:
            actions.append(
                PlannedAction(
                    name="navigate",
                    permission="navigation",
                    params={"url": start_url},
                )
            )

        lower = instruction.lower()

        if "login" in lower or "sign in" in lower:
            actions.extend(
                [
                    PlannedAction(
                        name="type",
                        permission="form_fill",
                        params={"selector": "#email", "text": "{{EMAIL}}"},
                    ),
                    PlannedAction(
                        name="type",
                        permission="form_fill",
                        params={"selector": "#password", "text": "{{PASSWORD}}"},
                    ),
                    PlannedAction(
                        name="submit",
                        permission="submission",
                        params={"selector": "button[type=submit]"},
                    ),
                ]
            )

        if "invoice" in lower or "billing" in lower:
            actions.extend(
                [
                    PlannedAction(
                        name="click",
                        permission="navigation",
                        params={"selector": "a[href*='invoice'], a[href*='billing']"},
                    ),
                    PlannedAction(
                        name="extract_text",
                        permission="read_only",
                        params={"selector": "body"},
                    ),
                    PlannedAction(
                        name="screenshot",
                        permission="read_only",
                        params={"name": "invoice-page"},
                    ),
                ]
            )

        if not actions:
            actions.append(
                PlannedAction(
                    name="screenshot",
                    permission="read_only",
                    params={"name": "landing-page"},
                )
            )

        return actions
