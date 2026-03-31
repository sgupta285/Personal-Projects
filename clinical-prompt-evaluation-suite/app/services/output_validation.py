from pydantic import ValidationError

from app.schemas import ClinicalSummarySchema


def validate_structured_output(output: dict) -> tuple[bool, list[str], dict]:
    try:
        validated = ClinicalSummarySchema.model_validate(output)
        return True, [], validated.model_dump()
    except ValidationError as exc:
        issues = []
        for error in exc.errors():
            loc = ".".join(str(part) for part in error.get("loc", []))
            issues.append(f"{loc}: {error.get('msg')}")
        return False, issues, output
