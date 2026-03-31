from __future__ import annotations

import hashlib
import random
import re
from dataclasses import dataclass


@dataclass
class GenerationRequest:
    system_prompt: str
    input_text: str
    provider: str
    model_name: str
    temperature: float = 0.2


class BaseProvider:
    def generate_structured_output(self, request: GenerationRequest) -> dict:
        raise NotImplementedError


class MockProvider(BaseProvider):
    def _extract_member_id(self, text: str) -> str:
        match = re.search(r"(member|patient)\s*id[:#]?\s*([A-Za-z0-9-]+)", text, re.IGNORECASE)
        return match.group(2) if match else "UNKNOWN"

    def _extract_date(self, text: str) -> str:
        match = re.search(r"(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", text)
        return match.group(1) if match else "1970-01-01"

    def _infer_service(self, text: str) -> str:
        lowered = text.lower()
        if "mri" in lowered:
            return "Lumbar spine MRI"
        if "physical therapy" in lowered:
            return "Physical therapy"
        if "ct" in lowered:
            return "CT scan"
        return "Utilization review request"

    def _risk_flags(self, text: str) -> list[str]:
        flags = []
        lowered = text.lower()
        for phrase, label in [
            ("fall risk", "Fall risk"),
            ("opioid", "Opioid exposure"),
            ("poorly controlled", "Poor symptom control"),
            ("multiple er visits", "High recent utilization"),
        ]:
            if phrase in lowered:
                flags.append(label)
        return flags

    def generate_structured_output(self, request: GenerationRequest) -> dict:
        text = request.input_text
        digest = hashlib.sha256((request.system_prompt + text).encode("utf-8")).hexdigest()
        random.seed(int(digest[:8], 16))
        service = self._infer_service(text)
        approval_evidence = []
        denial_evidence = []
        if "failed conservative therapy" in text.lower():
            approval_evidence.append("Failed conservative therapy documented.")
        if "neurologic deficit" in text.lower():
            approval_evidence.append("Neurologic deficit is documented.")
        if "insufficient imaging history" in text.lower():
            denial_evidence.append("Insufficient imaging history for escalation.")
        if "no red flag symptoms" in text.lower():
            denial_evidence.append("No red flag symptoms documented.")
        follow_up = []
        if not approval_evidence:
            follow_up.append("Clarify prior conservative management and duration.")
        if "pain score" not in text.lower():
            follow_up.append("Document current pain score and functional limitation.")
        summary = (
            f"Structured review for {service}. The note highlights the presenting concern, supporting evidence, "
            f"and outstanding documentation gaps needed for a defensible utilization decision."
        )
        return {
            "member_id": self._extract_member_id(text),
            "encounter_date": self._extract_date(text),
            "requested_service": service,
            "primary_reason": "Persistent symptoms requiring utilization review summary.",
            "evidence_for_approval": approval_evidence,
            "evidence_for_denial": denial_evidence,
            "risk_flags": self._risk_flags(text),
            "follow_up_questions": follow_up,
            "summary": summary,
            "confidence": round(0.72 + random.random() * 0.18, 2),
        }


class OpenAIProvider(BaseProvider):
    def generate_structured_output(self, request: GenerationRequest) -> dict:
        raise NotImplementedError(
            "OpenAI provider wiring is intentionally left as a guarded extension point. "
            "Use the mock provider by default or add your API integration in app/services/llm_clients.py."
        )


class AnthropicProvider(BaseProvider):
    def generate_structured_output(self, request: GenerationRequest) -> dict:
        raise NotImplementedError(
            "Anthropic provider wiring is intentionally left as a guarded extension point. "
            "Use the mock provider by default or add your API integration in app/services/llm_clients.py."
        )


def get_provider(provider_name: str) -> BaseProvider:
    provider_name = provider_name.lower()
    if provider_name == "mock":
        return MockProvider()
    if provider_name == "openai":
        return OpenAIProvider()
    if provider_name == "anthropic":
        return AnthropicProvider()
    raise ValueError(f"Unsupported provider: {provider_name}")
