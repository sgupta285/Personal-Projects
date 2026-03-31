from app.services.llm_clients import GenerationRequest, MockProvider


def test_mock_provider_returns_schema_like_output():
    provider = MockProvider()
    result = provider.generate_structured_output(
        GenerationRequest(
            system_prompt="test",
            input_text=(
                "Member ID: M-101. Encounter date: 2026-02-02. Request for lumbar MRI. "
                "Failed conservative therapy noted. Fall risk documented."
            ),
            provider="mock",
            model_name="demo-model",
        )
    )
    assert result["member_id"] == "M-101"
    assert result["requested_service"] == "Lumbar spine MRI"
    assert "Fall risk" in result["risk_flags"]
