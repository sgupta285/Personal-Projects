"""
ClearCause - Report Export Lambda
Generates downloadable PDF reports from analysis results.
"""
import json
import os
import boto3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
BUCKET = os.environ.get("DOCUMENTS_BUCKET", "clearcause-documents")
RESULTS_TABLE = dynamodb.Table(os.environ.get("RESULTS_TABLE", "clearcause-results"))

# Colors
TEAL = HexColor("#0d9488")
DARK = HexColor("#0f172a")
RED = HexColor("#ef4444")
AMBER = HexColor("#f59e0b")
GREEN = HexColor("#10b981")
GRAY = HexColor("#64748b")
LIGHT_GRAY = HexColor("#f1f5f9")

RISK_COLORS = {"high": RED, "medium": AMBER, "low": GREEN}


def lambda_handler(event, context):
    """Generate PDF report for a completed analysis."""
    try:
        params = event.get("queryStringParameters", {})
        job_id = params.get("job_id")
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]

        if not job_id:
            return _response(400, {"error": "job_id is required"})

        # Fetch analysis results
        result = RESULTS_TABLE.get_item(Key={"job_id": job_id})
        if "Item" not in result:
            return _response(404, {"error": "Analysis not found"})

        report = result["Item"]
        if report["user_id"] != user_id:
            return _response(403, {"error": "Access denied"})

        # Generate PDF
        pdf_key = f"exports/{user_id}/{job_id}/ClearCause_Report.pdf"
        pdf_path = f"/tmp/{job_id}.pdf"
        _generate_pdf(report, pdf_path)

        # Upload to S3
        with open(pdf_path, "rb") as f:
            s3.put_object(
                Bucket=BUCKET,
                Key=pdf_key,
                Body=f.read(),
                ContentType="application/pdf",
                ServerSideEncryption="aws:kms",
            )

        # Generate presigned URL (1 hour expiry)
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": pdf_key},
            ExpiresIn=3600,
        )

        return _response(200, {"download_url": url, "expires_in": 3600})

    except Exception as e:
        print(f"Report generation error: {str(e)}")
        return _response(500, {"error": "Failed to generate report"})


def _generate_pdf(report: dict, output_path: str):
    """Build the PDF report using ReportLab."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("Title2", parent=styles["Title"], fontSize=22, textColor=DARK, spaceAfter=6))
    styles.add(ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=11, textColor=GRAY, spaceAfter=20))
    styles.add(ParagraphStyle("SectionHead", parent=styles["Heading2"], fontSize=14, textColor=TEAL, spaceBefore=18, spaceAfter=8))
    styles.add(ParagraphStyle("BodyGray", parent=styles["Normal"], fontSize=10, textColor=DARK, leading=14, spaceAfter=6))
    styles.add(ParagraphStyle("Small", parent=styles["Normal"], fontSize=8, textColor=GRAY))
    styles.add(ParagraphStyle("RiskHigh", parent=styles["Normal"], fontSize=10, textColor=RED, leading=14))
    styles.add(ParagraphStyle("RiskMed", parent=styles["Normal"], fontSize=10, textColor=AMBER, leading=14))
    styles.add(ParagraphStyle("RiskLow", parent=styles["Normal"], fontSize=10, textColor=GREEN, leading=14))

    elements = []

    # Header
    elements.append(Paragraph("ClearCause Contract Analysis Report", styles["Title2"]))
    elements.append(Paragraph(
        f"{report['file_name']} · Analyzed {report.get('analyzed_at', 'N/A')}",
        styles["Subtitle"]
    ))
    elements.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY, spaceAfter=16))

    # Risk Score Summary
    risk = report.get("risk", {})
    elements.append(Paragraph("Risk Overview", styles["SectionHead"]))
    risk_data = [
        ["Overall Score", "Risk Level", "High Risk", "Medium Risk", "Low Risk"],
        [
            str(risk.get("score", "N/A")),
            str(risk.get("level", "N/A")).upper(),
            str(risk.get("high_count", 0)),
            str(risk.get("medium_count", 0)),
            str(risk.get("low_count", 0)),
        ],
    ]
    risk_table = Table(risk_data, colWidths=[1.3 * inch] * 5)
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 12))

    # Executive Summary
    elements.append(Paragraph("Executive Summary", styles["SectionHead"]))
    elements.append(Paragraph(report.get("executive_summary", "No summary available."), styles["BodyGray"]))

    # Clauses
    elements.append(Paragraph("Detected Clauses", styles["SectionHead"]))
    for clause in report.get("clauses", []):
        risk_style = {"high": "RiskHigh", "medium": "RiskMed", "low": "RiskLow"}.get(clause.get("risk_level", "low"), "BodyGray")
        elements.append(Paragraph(
            f"<b>{clause['label']}</b> [{clause.get('risk_level', 'unknown').upper()} RISK] — {clause.get('section_ref', '')}",
            styles[risk_style]
        ))
        elements.append(Paragraph(clause.get("summary", ""), styles["BodyGray"]))
        if clause.get("what_to_ask"):
            elements.append(Paragraph(f"<i>💡 Ask: {clause['what_to_ask']}</i>", styles["Small"]))
        elements.append(Spacer(1, 8))

    # Recommendations
    recs = report.get("recommendations", [])
    if recs:
        elements.append(Paragraph("Recommendations", styles["SectionHead"]))
        for i, rec in enumerate(recs, 1):
            elements.append(Paragraph(f"{i}. {rec}", styles["BodyGray"]))

    # Disclaimer
    elements.append(Spacer(1, 24))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=8))
    elements.append(Paragraph(
        "⚠️ This report is for informational purposes only and does not constitute legal advice. "
        "Consult a qualified attorney for your specific situation. Generated by ClearCause AI.",
        styles["Small"]
    ))

    doc.build(elements)


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }
