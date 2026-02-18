"""
Circuit breaker pattern for model inference reliability.
States: CLOSED (normal) -> OPEN (failing) -> HALF_OPEN (testing recovery).
"""

import time
import enum
import threading
import structlog

from app.config import settings

logger = structlog.get_logger()


class CircuitState(str, enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = settings.cb_failure_threshold,
        recovery_timeout: int = settings.cb_recovery_timeout,
        half_open_max_calls: int = settings.cb_half_open_max_calls,
    ):
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max_calls = half_open_max_calls
        self._last_failure_time: float = 0
        self._half_open_calls = 0
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                if time.time() - self._last_failure_time >= self._recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                    logger.info("circuit_half_open")
            return self._state

    @property
    def is_call_allowed(self) -> bool:
        state = self.state
        if state == CircuitState.CLOSED:
            return True
        if state == CircuitState.HALF_OPEN:
            with self._lock:
                return self._half_open_calls < self._half_open_max_calls
        return False  # OPEN

    def record_success(self):
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                self._half_open_calls += 1
                if self._success_count >= self._half_open_max_calls:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    logger.info("circuit_closed", reason="recovery_success")
            else:
                self._failure_count = max(0, self._failure_count - 1)

    def record_failure(self):
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._half_open_calls = 0
                logger.warning("circuit_open", reason="half_open_failure")
            elif self._failure_count >= self._failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(
                    "circuit_open",
                    reason="threshold_exceeded",
                    failures=self._failure_count,
                )

    def get_status(self) -> dict:
        return {
            "state": self.state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self._failure_threshold,
            "recovery_timeout_seconds": self._recovery_timeout,
        }

    def reset(self):
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._half_open_calls = 0
            logger.info("circuit_reset")


circuit_breaker = CircuitBreaker()
