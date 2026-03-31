
from app.services.layout import RawTextBlock, classify_blocks, infer_sections, reading_order


def test_reading_order_respects_columns():
    blocks = [
        RawTextBlock("a", 1, "Left 1", (10, 10, 100, 20), 11, 600, 800),
        RawTextBlock("b", 1, "Left 2", (10, 40, 100, 50), 11, 600, 800),
        RawTextBlock("c", 1, "Right 1", (340, 15, 430, 25), 11, 600, 800),
    ]
    ordered = reading_order(blocks)
    assert [block.id for block in ordered] == ["a", "b", "c"]


def test_sections_follow_heading_blocks():
    raw_blocks = [
        RawTextBlock("h1", 1, "SUMMARY", (10, 100, 120, 120), 16, 600, 800),
        RawTextBlock("p1", 1, "The first paragraph.", (10, 130, 300, 180), 11, 600, 800),
        RawTextBlock("h2", 1, "AUTHORIZATION TABLE", (10, 230, 220, 250), 15, 600, 800),
    ]
    layout_blocks = classify_blocks(raw_blocks, table_regions={})
    sections = infer_sections(layout_blocks)
    assert sections[0].title == "SUMMARY"
    assert sections[0].block_ids[0] == "h1"
    assert len(sections) == 2
