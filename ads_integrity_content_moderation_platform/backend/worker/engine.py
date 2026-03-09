from dataclasses import asdict, dataclass

from app.core.config import settings
from worker.classifier import score_payload
from worker.rules import evaluate_rules


@dataclass
class ModerationResult:
    rule_score: float
    model_score: float
    risk_score: float
    decision: str
    policy_hits: list[str]
    review_reason: str | None

    def to_dict(self) -> dict:
        return asdict(self)


def combine_scores(rule_score: float, model_score: float) -> float:
    weighted = (rule_score * 0.6) + (model_score * 0.4)
    if rule_score > 0.4 and model_score > 0.65:
        weighted += 0.1
    return round(min(weighted, 1.0), 4)


def decide_status(risk_score: float) -> str:
    if risk_score >= settings.risk_block_threshold:
        return "blocked"
    if risk_score >= settings.risk_review_threshold:
        return "in_review"
    return "approved"


def moderate(payload: dict) -> ModerationResult:
    rule_result = evaluate_rules(payload)
    model_score = score_payload(payload)
    risk_score = combine_scores(rule_result.score, model_score)
    decision = decide_status(risk_score)

    reason = rule_result.reason
    if decision == "blocked" and not reason:
        reason = "Combined model and rules score crossed the auto-block threshold."
    elif decision == "in_review" and not reason:
        reason = "Moderation score indicates the ad should be reviewed by a human."
    elif decision == "approved":
        reason = "No strong fraud or policy signals were detected."

    return ModerationResult(
        rule_score=round(rule_result.score, 4),
        model_score=round(model_score, 4),
        risk_score=risk_score,
        decision=decision,
        policy_hits=rule_result.policy_hits,
        review_reason=reason,
    )
