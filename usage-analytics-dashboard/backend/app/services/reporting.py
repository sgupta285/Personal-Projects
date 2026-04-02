import csv
import io
from datetime import date

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


class ReportBuilder:
    def build_csv(self, rows: list[dict]) -> bytes:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()) if rows else ["bucket_start", "request_units"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        return buffer.getvalue().encode("utf-8")

    def build_pdf(self, workspace_id: str, start_date: date, end_date: date, totals: dict, breakdown_rows: list[dict]) -> bytes:
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        pdf.setTitle(f"Usage report - {workspace_id}")
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(0.75 * inch, height - 0.9 * inch, f"Usage report for {workspace_id}")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(0.75 * inch, height - 1.25 * inch, f"Reporting window: {start_date.isoformat()} to {end_date.isoformat()}")
        y = height - 1.75 * inch
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(0.75 * inch, y, "Summary")
        y -= 0.25 * inch
        pdf.setFont("Helvetica", 11)
        for key, value in totals.items():
            pdf.drawString(0.9 * inch, y, f"{key}: {value}")
            y -= 0.22 * inch
        y -= 0.12 * inch
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(0.75 * inch, y, "Top breakdown rows")
        y -= 0.28 * inch
        pdf.setFont("Helvetica", 10)
        for row in breakdown_rows[:10]:
            pdf.drawString(0.9 * inch, y, f"{row['group_value']}: units={row['request_units']}, cost=${row['total_cost_usd']}")
            y -= 0.2 * inch
            if y < 0.9 * inch:
                pdf.showPage()
                y = height - 0.9 * inch
                pdf.setFont("Helvetica", 10)
        pdf.save()
        return buffer.getvalue()


report_builder = ReportBuilder()
