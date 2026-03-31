from app.runtime.planner import RuleBasedPlanner


def test_login_instruction_generates_login_actions() -> None:
    planner = RuleBasedPlanner()
    plan = planner.build_plan(
        "Log into the portal and inspect the latest invoice details.",
        "https://example.com/login",
    )
    action_names = [action.name for action in plan]
    assert "navigate" in action_names
    assert "type" in action_names
    assert "submit" in action_names
    assert "extract_text" in action_names


def test_generic_instruction_falls_back_to_screenshot() -> None:
    planner = RuleBasedPlanner()
    plan = planner.build_plan("Open the page and inspect it.", None)
    assert len(plan) == 1
    assert plan[0].name == "screenshot"
