import asyncio

from app.services.cache import PredictionCache


def test_memory_cache_round_trip():
    async def run():
        cache = PredictionCache()
        await cache.set("abc", {"value": 1})
        assert await cache.get("abc") == {"value": 1}
        await cache.clear()
        assert await cache.get("abc") is None

    asyncio.run(run())
