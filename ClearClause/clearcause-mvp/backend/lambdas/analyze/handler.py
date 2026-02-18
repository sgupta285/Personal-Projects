"""
ClearCause - Document Analysis Lambda
Core analysis pipeline: Extract → Chunk → Embed → Detect → Summarize → Score
Triggered by SQS messages from the upload handler.
"""
import json
import re
import os
import uuid
import boto3
import openai
from datetime import datetime
from typing import Optional

# ─── AWS Clients ───
s3 = boto3.client("s3")
textract = boto3.client("textract")
dynamodb = boto3.resource("dynamodb")

BUCKET = os.environ.get("DOCUMENTS_BUCKET", "clearcause-documents")
JOBS_TABLE = dynamodb.Table(os.environ.get("JOBS_TABLE", "clearcause-jobs"))
RESULTS_TABLE = dynamodb.Table(os.environ.get("RESULTS_TABLE", "clearcause-results"))

openai.api_key = os.environ.get("OPENAI_API_KEY")

# ─── Clause Taxonomy ───
CLAUSE_PATTERNS = {
    "arbitration": {
        "label": "Binding Arbitration",
        "keywords": ["arbitration", "arbitrate", "aaa ", "american arbitration", "waive.*jury", "class.?action.*waiv"],
        "risk_weight": 3,
        "category": "dispute_resolution",
    },
    "auto_renewal": {
        "label": "Auto-Renewal",
        "keywords": ["auto.?renew", "automatic.*renew", "renew.*automatically", "successive.*term", "evergreen"],
        "risk_weight": 2,
        "category": "term",
    },
    "liability_cap": {
        "label": "Liability Limitation",
        "keywords": ["limit.*liability", "liability.*limit", "aggregate.*liability", "not.*liable.*indirect", "consequential.*damage", "cap.*damages"],
        "risk_weight": 3,
        "category": "liability",
    },
    "data_sharing": {
        "label": "Data Sharing with Third Parties",
        "keywords": ["share.*personal.*information", "third.?part.*data", "advertising.*partner", "analytics.*provider", "share.*data.*with"],
        "risk_weight": 2,
        "category": "privacy",
    },
    "unilateral_changes": {
        "label": "Unilateral Modification",
        "keywords": ["right to modify", "change.*terms.*any.*time", "sole discretion.*modify", "continued use.*acceptance", "modify.*without.*notice"],
        "risk_weight": 3,
        "category": "term",
    },
    "termination_without_cause": {
        "label": "Termination Without Cause",
        "keywords": ["terminat.*any.*reason", "terminat.*without.*cause", "terminat.*convenience", "terminat.*at.*will"],
        "risk_weight": 2,
        "category": "term",
    },
    "ip_assignment": {
        "label": "IP & Content Rights",
        "keywords": ["intellectual property.*assign", "grant.*license.*content", "worldwide.*royalty.?free", "perpetual.*license", "irrevocable.*license"],
        "risk_weight": 1,
        "category": "ip",
    },
    "indemnification": {
        "label": "Indemnification",
        "keywords": ["indemnif", "hold.*harmless", "defend.*against.*claim"],
        "risk_weight": 2,
        "category": "liability",
    },
    "force_majeure": {
        "label": "Force Majeure",
        "keywords": ["force majeure", "act of god", "beyond.*reasonable.*control"],
        "risk_weight": 1,
        "category": "liability",
    },
    "non_compete": {
        "label": "Non-Compete / Non-Solicitation",
        "keywords": ["non.?compet", "non.?solicit", "restrict.*competing", "not.*engage.*similar"],
        "risk_weight": 3,
        "category": "restrictions",
    },
    "governing_law": {
        "label": "Governing Law & Venue",
        "keywords": ["governing law", "governed by.*laws", "exclusive.*jurisdiction", "venue.*shall be"],
        "risk_weight": 1,
        "category": "dispute_resolution",
    },
    "data_retention": {
        "label": "Data Retention After Termination",
        "keywords": ["retain.*data.*after", "data.*surviv.*termination", "delete.*upon.*request", "retain.*information.*following"],
        "risk_weight": 2,
        "category": "privacy",
    },
}


# ─── Step 1: Extract Text ───
def extract_text(s3_key: str) -> str:
    """Extract text from PDF using Textract, with fallback to PyMuPDF."""
    try:
        response = textract.start_document_text_detection(
            DocumentLocation={"S3Object": {"Bucket": BUCKET, "Name": s3_key}}
        )
        job_id = response["JobId"]

        # Poll for completion
        import time
        while True:
            result = textract.get_document_text_detection(JobId=job_id)
            if result["JobStatus"] in ("SUCCEEDED", "FAILED"):
                break
            time.sleep(2)

        if result["JobStatus"] == "FAILED":
            raise Exception("Textract extraction failed")

        # Aggregate text blocks
        text_blocks = []
        for block in result.get("Blocks", []):
            if block["BlockType"] == "LINE":
                text_blocks.append(block["Text"])

        return "\n".join(text_blocks)

    except Exception as e:
        print(f"Textract failed, attempting PyMuPDF fallback: {e}")
        return _extract_with_pymupdf(s3_key)


def _extract_with_pymupdf(s3_key: str) -> str:
    """Fallback PDF extraction using PyMuPDF."""
    import fitz  # PyMuPDF

    obj = s3.get_object(Bucket=BUCKET, Key=s3_key)
    pdf_bytes = obj["Body"].read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


# ─── Step 2: Chunk Text ───
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """Semantic-aware chunking by paragraph boundaries."""
    paragraphs = re.split(r"\n{2,}", text)
    chunks = []
    current_chunk = ""
    chunk_start = 0
    char_pos = 0

    for para in paragraphs:
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "start": chunk_start,
                "end": char_pos,
                "index": len(chunks),
            })
            # Overlap: keep last portion
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else ""
            current_chunk = overlap_text + para
            chunk_start = char_pos - len(overlap_text)
        else:
            current_chunk += "\n\n" + para
        char_pos += len(para) + 2

    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "start": chunk_start,
            "end": char_pos,
            "index": len(chunks),
        })

    return chunks


# ─── Step 3: Detect Clauses ───
def detect_clauses(chunks: list[dict]) -> list[dict]:
    """Detect clause types using regex + keyword matching."""
    detected = []

    for chunk in chunks:
        text_lower = chunk["text"].lower()
        for clause_id, pattern in CLAUSE_PATTERNS.items():
            for keyword in pattern["keywords"]:
                if re.search(keyword, text_lower):
                    # Check for duplicates
                    existing = [d for d in detected if d["clause_type"] == clause_id]
                    if not existing:
                        detected.append({
                            "clause_type": clause_id,
                            "label": pattern["label"],
                            "category": pattern["category"],
                            "risk_weight": pattern["risk_weight"],
                            "matched_keyword": keyword,
                            "source_chunk": chunk["index"],
                            "source_text": chunk["text"][:500],
                            "char_start": chunk["start"],
                            "char_end": chunk["end"],
                        })
                    break  # One match per clause per chunk is sufficient

    return detected


# ─── Step 4: Summarize with LLM ───
def summarize_clause(clause: dict) -> dict:
    """Generate plain-language summary for a detected clause using GPT-4o-mini."""
    prompt = f"""You are a legal document simplifier. Summarize this contract clause in plain English 
at an 8th-grade reading level. Be neutral and educational, not fear-mongering.

Clause Type: {clause['label']}
Original Text: {clause['source_text']}

Respond in JSON format:
{{
    "summary": "2-3 sentence plain English explanation of what this means for the signer",
    "risk_level": "high|medium|low",
    "risk_explanation": "One sentence explaining WHY this risk level",
    "what_to_ask": "A specific question the signer should ask about this clause",
    "key_terms": ["list", "of", "important", "terms"]
}}"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a legal document simplifier. Output only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=400,
        )
        content = response.choices[0].message.content.strip()
        # Strip markdown fences if present
        content = re.sub(r"```json\s*", "", content)
        content = re.sub(r"```\s*$", "", content)
        return json.loads(content)

    except Exception as e:
        print(f"LLM summarization failed for {clause['label']}: {e}")
        return {
            "summary": f"This clause relates to {clause['label'].lower()}. Review the original text carefully.",
            "risk_level": _weight_to_risk(clause["risk_weight"]),
            "risk_explanation": "Could not generate detailed analysis.",
            "what_to_ask": "Ask the other party to explain this clause in plain language.",
            "key_terms": [],
        }


def _weight_to_risk(weight: int) -> str:
    if weight >= 3:
        return "high"
    elif weight >= 2:
        return "medium"
    return "low"


# ─── Step 5: Score Risk ───
def calculate_risk_score(clauses: list[dict]) -> dict:
    """Calculate overall document risk score."""
    if not clauses:
        return {"score": 0, "level": "low", "breakdown": {}}

    total_weight = sum(c.get("risk_weight", 1) for c in clauses)
    max_possible = len(CLAUSE_PATTERNS) * 3  # max weight per clause type
    raw_score = (total_weight / max_possible) * 100

    high_count = sum(1 for c in clauses if c.get("risk_level", _weight_to_risk(c.get("risk_weight", 1))) == "high")
    med_count = sum(1 for c in clauses if c.get("risk_level", _weight_to_risk(c.get("risk_weight", 1))) == "medium")

    # Weighted score
    score = min(100, int(raw_score + high_count * 10 + med_count * 3))

    level = "low"
    if score >= 65 or high_count >= 3:
        level = "high"
    elif score >= 35 or high_count >= 1:
        level = "medium"

    return {
        "score": score,
        "level": level,
        "high_count": high_count,
        "medium_count": med_count,
        "low_count": len(clauses) - high_count - med_count,
        "total_clauses": len(clauses),
    }


# ─── Step 6: Generate Executive Summary ───
def generate_executive_summary(clauses: list[dict], risk: dict, file_name: str) -> str:
    """Generate an overall document summary."""
    clause_summaries = "\n".join(
        f"- {c['label']} ({c.get('risk_level', 'unknown')} risk): {c.get('summary', 'N/A')}"
        for c in clauses
    )
    prompt = f"""Summarize this contract analysis in 3-4 sentences at an 8th-grade reading level.
Be educational and neutral.

Document: {file_name}
Overall Risk Score: {risk['score']}/100 ({risk['level']})
High-risk clauses: {risk['high_count']}
Total clauses found: {risk['total_clauses']}

Clauses found:
{clause_summaries}

Write a plain-English summary a non-lawyer can understand."""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Executive summary generation failed: {e}")
        return f"This document contains {risk['total_clauses']} notable clauses, including {risk['high_count']} high-risk items. Review the detailed analysis below."


# ─── Main Handler ───
def lambda_handler(event, context):
    """Process SQS messages for document analysis."""
    for record in event["Records"]:
        message = json.loads(record["body"])
        job_id = message["job_id"]
        user_id = message["user_id"]
        s3_key = message["s3_key"]
        file_name = message["file_name"]

        try:
            # Update status
            _update_job_status(job_id, "processing")

            # Pipeline
            print(f"[{job_id}] Step 1: Extracting text from {s3_key}")
            text = extract_text(s3_key)

            print(f"[{job_id}] Step 2: Chunking ({len(text)} chars)")
            chunks = chunk_text(text)

            print(f"[{job_id}] Step 3: Detecting clauses in {len(chunks)} chunks")
            detected = detect_clauses(chunks)

            print(f"[{job_id}] Step 4: Summarizing {len(detected)} clauses")
            for clause in detected:
                summary_data = summarize_clause(clause)
                clause.update(summary_data)

            print(f"[{job_id}] Step 5: Calculating risk score")
            risk = calculate_risk_score(detected)

            print(f"[{job_id}] Step 6: Generating executive summary")
            exec_summary = generate_executive_summary(detected, risk, file_name)

            # Build result
            result = {
                "job_id": job_id,
                "user_id": user_id,
                "file_name": file_name,
                "analyzed_at": datetime.utcnow().isoformat(),
                "document_stats": {
                    "char_count": len(text),
                    "chunk_count": len(chunks),
                    "estimated_pages": max(1, len(text) // 3000),
                },
                "risk": risk,
                "executive_summary": exec_summary,
                "clauses": [
                    {
                        "id": str(uuid.uuid4())[:8],
                        "type": c["clause_type"],
                        "label": c["label"],
                        "category": c["category"],
                        "risk_level": c.get("risk_level", _weight_to_risk(c["risk_weight"])),
                        "summary": c.get("summary", ""),
                        "risk_explanation": c.get("risk_explanation", ""),
                        "what_to_ask": c.get("what_to_ask", ""),
                        "key_terms": c.get("key_terms", []),
                        "source_text": c["source_text"],
                        "section_ref": f"§ Chunk {c['source_chunk'] + 1}",
                        "char_range": [c["char_start"], c["char_end"]],
                    }
                    for c in detected
                ],
                "recommendations": _generate_recommendations(detected, risk),
            }

            # Store results
            RESULTS_TABLE.put_item(Item=_sanitize_for_dynamo(result))

            # Store JSON report to S3
            report_key = f"reports/{user_id}/{job_id}/report.json"
            s3.put_object(
                Bucket=BUCKET,
                Key=report_key,
                Body=json.dumps(result, default=str),
                ContentType="application/json",
                ServerSideEncryption="aws:kms",
            )

            _update_job_status(job_id, "completed", report_key=report_key)
            print(f"[{job_id}] Analysis complete. Score: {risk['score']}/100")

        except Exception as e:
            print(f"[{job_id}] Analysis failed: {str(e)}")
            _update_job_status(job_id, "failed", error=str(e))
            raise


def _generate_recommendations(clauses: list[dict], risk: dict) -> list[str]:
    """Generate actionable recommendations based on detected clauses."""
    recs = []
    clause_types = {c["clause_type"] for c in clauses}

    if "arbitration" in clause_types:
        recs.append("Request an opt-out window for binding arbitration (many contracts allow 30-day opt-out)")
    if "unilateral_changes" in clause_types:
        recs.append("Ask for advance written notice (at least 30 days) before any material term changes")
    if "auto_renewal" in clause_types:
        recs.append("Set a calendar reminder 45 days before the renewal date to review or cancel")
    if "data_sharing" in clause_types:
        recs.append("Request a Data Processing Addendum (DPA) and opt-out of third-party data sharing")
    if "liability_cap" in clause_types:
        recs.append("Negotiate exceptions to the liability cap for data breaches and gross negligence")
    if "indemnification" in clause_types:
        recs.append("Push for mutual indemnification instead of one-sided obligations")
    if "termination_without_cause" in clause_types:
        recs.append("Negotiate pro-rated refunds for unused prepaid periods upon early termination")
    if risk["score"] >= 60:
        recs.append("Consider having an attorney review this document before signing")

    return recs[:6]


def _update_job_status(job_id: str, status: str, report_key: str = None, error: str = None):
    """Update job status in DynamoDB."""
    update_expr = "SET #s = :s, updated_at = :t"
    expr_values = {":s": status, ":t": datetime.utcnow().isoformat()}
    expr_names = {"#s": "status"}

    if report_key:
        update_expr += ", report_key = :r"
        expr_values[":r"] = report_key
    if error:
        update_expr += ", error_message = :e"
        expr_values[":e"] = error

    JOBS_TABLE.update_item(
        Key={"job_id": job_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values,
        ExpressionAttributeNames=expr_names,
    )


def _sanitize_for_dynamo(obj):
    """Convert floats to Decimal for DynamoDB compatibility."""
    from decimal import Decimal
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: _sanitize_for_dynamo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_for_dynamo(i) for i in obj]
    return obj
