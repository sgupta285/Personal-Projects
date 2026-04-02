import time
from collections import defaultdict, deque
from fastapi import HTTPException, status


class Limiter:
    def __init__(self) -> None:
        self.minute_buckets: dict[str, deque[float]] = defaultdict(deque)
        self.daily_counts: dict[str, tuple[int, float]] = {}

    def enforce(self, key: str, per_minute: int, daily_quota: int) -> None:
        now = time.time()
        bucket = self.minute_buckets[key]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={'code': 'rate_limited', 'message': 'Rate limit exceeded'},
                headers={'Retry-After': '60'},
            )
        bucket.append(now)

        count, reset_at = self.daily_counts.get(key, (0, now + 86400))
        if now > reset_at:
            count, reset_at = 0, now + 86400
        count += 1
        if count > daily_quota:
            self.daily_counts[key] = (count, reset_at)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={'code': 'quota_exceeded', 'message': 'Daily quota exceeded'},
            )
        self.daily_counts[key] = (count, reset_at)


limiter = Limiter()
