from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    reason: str | None = None


class PermissionPolicy:
    SAFE_ACTIONS = {"read_only", "navigation", "form_fill"}
    DESTRUCTIVE_ACTIONS = {"submission"}

    def check(self, permission: str, dry_run: bool) -> PermissionDecision:
        if permission in self.SAFE_ACTIONS:
            return PermissionDecision(True, None)

        if permission in self.DESTRUCTIVE_ACTIONS and dry_run:
            return PermissionDecision(
                False,
                "Submission-style actions are blocked in dry-run mode.",
            )

        if permission in self.DESTRUCTIVE_ACTIONS and not dry_run:
            return PermissionDecision(True, None)

        return PermissionDecision(False, f"Unknown permission class: {permission}")
