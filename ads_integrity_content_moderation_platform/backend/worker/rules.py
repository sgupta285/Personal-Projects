from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class RuleResult:
    score: float
    policy_hits: list[str]
    reason: str | None = None


HIGH_RISK_KEYWORDS = {
    "free money": 0.30,
    "guaranteed returns": 0.28,
    "crypto doubling": 0.35,
    "no credit check": 0.22,
    "miracle cure": 0.28,
    "act now": 0.08,
    "limited time": 0.08,
    "before and after": 0.18,
    "secret formula": 0.16,
    "dm for earnings": 0.22,
    "instant approval": 0.15,
    "earn $": 0.18,
}

PROHIBITED_CATEGORIES = {
    "adult": 0.40,
    "gambling": 0.30,
    "weapons": 0.45,
    "counterfeit": 0.50,
}

SUSPICIOUS_TLDS = {".ru", ".zip", ".click", ".xyz"}


def evaluate_rules(payload: dict) -> RuleResult:
    text_parts = [
        payload.get("title", ""),
        payload.get("body", ""),
        payload.get("call_to_action", ""),
        payload.get("creative_text", ""),
        " ".join(payload.get("creative_tags", []) or []),
    ]
    full_text = " ".join(text_parts).lower()

    score = 0.0
    hits: list[str] = []

    for phrase, weight in HIGH_RISK_KEYWORDS.items():
        if phrase in full_text:
            score += weight
            hits.append(f"copy:{phrase}")

    category = str(payload.get("category", "")).strip().lower()
    if category in PROHIBITED_CATEGORIES:
        score += PROHIBITED_CATEGORIES[category]
        hits.append(f"category:{category}")

    url = payload.get("landing_page_url", "")
    hostname = urlparse(url).hostname or ""
    if hostname.count("-") >= 3:
        score += 0.12
        hits.append("url:excessive-hyphens")
    if any(hostname.endswith(tld) for tld in SUSPICIOUS_TLDS):
        score += 0.18
        hits.append("url:suspicious-tld")
    if "bit.ly" in url or "tinyurl" in url:
        score += 0.12
        hits.append("url:shortener")

    if payload.get("budget_cents", 0) > 500_000 and "guaranteed" in full_text:
        score += 0.10
        hits.append("budget:high-spend-risky-copy")

    geo_targets = payload.get("geo_targets", []) or []
    if len(geo_targets) > 15:
        score += 0.05
        hits.append("targeting:wide-blast-radius")

    reason = None
    if hits:
        reason = "Rule engine found policy-sensitive patterns in copy, category, or destination URL."

    return RuleResult(score=min(score, 1.0), policy_hits=hits, reason=reason)
