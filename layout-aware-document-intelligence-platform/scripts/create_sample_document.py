
from __future__ import annotations

from pathlib import Path

import fitz


def main() -> None:
    output_dir = Path("sample_data")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "sample-insurance-summary.pdf"

    document = fitz.open()
    page = document.new_page(width=595, height=842)

    page.insert_text((50, 40), "Acme Benefits, Inc.", fontsize=11)
    page.insert_text((50, 85), "UTILIZATION REVIEW SUMMARY", fontsize=18)
    page.insert_text((50, 115), "Patient: Jamie Doe", fontsize=12)
    page.insert_text((50, 135), "Member ID: 48291812", fontsize=12)
    page.insert_text((50, 155), "Review Date: March 29, 2026", fontsize=12)
    page.insert_text((50, 195), "CLINICAL OVERVIEW", fontsize=14)
    page.insert_textbox(
        fitz.Rect(50, 215, 540, 310),
        "The patient presented with persistent knee pain after a sports injury. "
        "Physical therapy was attempted for six weeks with limited improvement. "
        "MRI findings show a partial meniscal tear. Conservative management remains documented.",
        fontsize=11,
    )
    page.insert_text((50, 335), "AUTHORIZATION TABLE", fontsize=14)
    shape = page.new_shape()
    top = 365
    left = 50
    col_widths = [160, 140, 140]
    row_height = 28
    total_width = sum(col_widths)
    total_height = row_height * 4
    shape.draw_rect(fitz.Rect(left, top, left + total_width, top + total_height))
    x = left
    for width in col_widths[:-1]:
        x += width
        shape.draw_line((x, top), (x, top + total_height))
    for row in range(1, 4):
        y = top + row * row_height
        shape.draw_line((left, y), (left + total_width, y))
    shape.finish(width=1)
    shape.commit()

    headers = ["Service", "Status", "Amount"]
    rows = [
        ["Orthopedic Consult", "Approved", "$180.00"],
        ["MRI", "Approved", "$1,240.00"],
        ["Surgery", "Pending", "$8,900.00"],
    ]
    x = left + 8
    y = top + 18
    for idx, header in enumerate(headers):
        page.insert_text((x, y), header, fontsize=10)
        x += col_widths[idx]
    for row_index, row in enumerate(rows, start=1):
        x = left + 8
        y = top + row_index * row_height + 18
        for idx, value in enumerate(row):
            page.insert_text((x, y), value, fontsize=10)
            x += col_widths[idx]

    page.insert_text((50, 805), "Page 1 of 1", fontsize=10)
    document.save(output_path.as_posix())
    document.close()
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
