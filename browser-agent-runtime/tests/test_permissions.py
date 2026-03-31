from app.runtime.permissions import PermissionPolicy


def test_safe_actions_are_allowed_in_dry_run() -> None:
    policy = PermissionPolicy()
    decision = policy.check("navigation", dry_run=True)
    assert decision.allowed is True
    assert decision.reason is None


def test_submission_is_blocked_in_dry_run() -> None:
    policy = PermissionPolicy()
    decision = policy.check("submission", dry_run=True)
    assert decision.allowed is False
    assert "dry-run" in decision.reason.lower()


def test_submission_allowed_when_not_dry_run() -> None:
    policy = PermissionPolicy()
    decision = policy.check("submission", dry_run=False)
    assert decision.allowed is True
