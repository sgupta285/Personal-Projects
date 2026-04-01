import asyncio

from app.schemas.prediction import FeaturePayload
from app.services.batching import DynamicBatcher


class StubModelRepo:
    def predict_scores(self, payloads):
        return [0.5 for _ in payloads]


def test_batcher_returns_scores():
    async def run():
        batcher = DynamicBatcher(model_repo=StubModelRepo())
        await batcher.start()
        payload = FeaturePayload(
            account_tenure_days=10,
            avg_session_seconds=200,
            prior_purchases=2,
            cart_additions_7d=3,
            email_click_rate=0.2,
            discount_sensitivity=0.3,
            inventory_score=0.9,
            device_trust_score=0.8,
        )
        score = await batcher.infer(payload)
        assert score == 0.5
        await batcher.stop()

    asyncio.run(run())
