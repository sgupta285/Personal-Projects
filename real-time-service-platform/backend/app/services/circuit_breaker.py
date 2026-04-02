import time
from dataclasses import dataclass
from enum import Enum

from app.core.config import get_settings
from app.observability.metrics import CIRCUIT_BREAKER_STATE


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    failure_threshold: int
    recovery_timeout: int
    failures: int = 0
    state: CircuitState = CircuitState.CLOSED
    last_failure_at: float = 0.0

    def allow_request(self) -> bool:
        if self.state == CircuitState.OPEN:
            if time.monotonic() - self.last_failure_at >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                CIRCUIT_BREAKER_STATE.set(2)
                return True
            return False
        return True

    def mark_success(self) -> None:
        self.failures = 0
        self.state = CircuitState.CLOSED
        CIRCUIT_BREAKER_STATE.set(0)

    def mark_failure(self) -> None:
        self.failures += 1
        self.last_failure_at = time.monotonic()
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            CIRCUIT_BREAKER_STATE.set(1)


settings = get_settings()
service_circuit_breaker = CircuitBreaker(
    failure_threshold=settings.circuit_breaker_failure_threshold,
    recovery_timeout=settings.circuit_breaker_recovery_timeout,
)
