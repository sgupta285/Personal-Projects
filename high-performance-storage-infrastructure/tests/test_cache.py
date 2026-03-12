from storageinfra.cache import MemoryCache


def test_memory_cache_hits_and_evictions():
    cache = MemoryCache(capacity_bytes=10)
    cache.set("a", b"12345")
    cache.set("b", b"67890")
    assert cache.get("a") == b"12345"
    cache.set("c", b"zzzzz")
    assert cache.stats.evictions >= 1
