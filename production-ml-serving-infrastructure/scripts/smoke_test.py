import asyncio

import httpx


async def main() -> None:
    async with httpx.AsyncClient(timeout=5.0) as client:
        health = await client.get("http://localhost:8000/health/live")
        print("live", health.status_code, health.json())
        prediction = await client.post(
            "http://localhost:8000/v1/predict",
            json={
                "request_id": "smoke-1",
                "features": {
                    "account_tenure_days": 180,
                    "avg_session_seconds": 700,
                    "prior_purchases": 6,
                    "cart_additions_7d": 9,
                    "email_click_rate": 0.22,
                    "discount_sensitivity": 0.66,
                    "inventory_score": 0.74,
                    "device_trust_score": 0.88,
                },
            },
        )
        print("predict", prediction.status_code, prediction.json())


if __name__ == "__main__":
    asyncio.run(main())
