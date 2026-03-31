
from app.services.comparison import compare_revisions, summarize_result


def test_summarize_result_counts_major_sections():
    result = {
        "pages": [1, 2],
        "blocks": [1, 2, 3],
        "sections": [1],
        "tables": [1],
        "entities": [1, 2],
        "warnings": [],
    }
    summary = summarize_result(result)
    assert summary["page_count"] == 2
    assert summary["entity_count"] == 2


def test_compare_revisions_reports_deltas():
    left = {"pages": [1], "blocks": [1], "sections": [], "tables": [], "entities": [], "warnings": []}
    right = {"pages": [1, 2], "blocks": [1, 2], "sections": [1], "tables": [], "entities": [1], "warnings": []}
    changes = compare_revisions(left, right)
    assert changes["page_count"]["delta"] == 1
    assert changes["section_count"]["to"] == 1
