from worker.rules import evaluate_rules


def test_rule_engine_flags_obvious_scam_copy():
    result = evaluate_rules(
        {
            "title": "Guaranteed returns in 24 hours",
            "body": "Free money with our crypto doubling system",
            "call_to_action": "Act now",
            "landing_page_url": "https://crypto-win-fast.xyz",
            "category": "finance",
            "creative_tags": ["urgent", "wealth"],
            "geo_targets": ["US"],
            "budget_cents": 100000,
        }
    )

    assert result.score > 0.5
    assert any(hit.startswith("copy:") for hit in result.policy_hits)
    assert "url:suspicious-tld" in result.policy_hits


def test_rule_engine_allows_normal_retail_ad():
    result = evaluate_rules(
        {
            "title": "Spring running shoes",
            "body": "Comfortable shoes with free shipping over $50.",
            "call_to_action": "Shop now",
            "landing_page_url": "https://example.com/running-shoes",
            "category": "retail",
            "creative_tags": ["footwear"],
            "geo_targets": ["US"],
            "budget_cents": 20000,
        }
    )

    assert result.score < 0.2
