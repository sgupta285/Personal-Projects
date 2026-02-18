"""
Monitoring: Prometheus metrics, latency tracking, degradation alerts.
"""

import time
from dataclasses import dataclass, field
from typing import List
import structlog

logger = structlog.get_logger()


@dataclass
class LatencyStats:
    count: int = 0
    total_ms: float = 0.0
    max_ms: float = 0.0
    min_ms: float = float("inf")
    p50_buffer: List[float] = field(default_factory=list)

    def record(self, ms: float):
        self.count += 1
        self.total_ms += ms
        self.max_ms = max(self.max_ms, ms)
        self.min_ms = min(self.min_ms, ms)
        self.p50_buffer.append(ms)
        if len(self.p50_buffer) > 10000:
            self.p50_buffer = self.p50_buffer[-5000:]

    @property
    def avg_ms(self) -> float:
        return self.total_ms / self.count if self.count > 0 else 0.0

    @property
    def p95_ms(self) -> float:
        if not self.p50_buffer:
            return 0.0
        s = sorted(self.p50_buffer)
        idx = int(len(s) * 0.95)
        return s[min(idx, len(s) - 1)]


class MonitoringService:
    """Tracks system health, latency, and triggers degradation alerts."""

    def __init__(self, alert_latency_ms=100.0, alert_drawdown_pct=0.10):
        self.signal_latency = LatencyStats()
        self.tick_latency = LatencyStats()
        self.alerts: List[str] = []
        self.alert_latency_ms = alert_latency_ms
        self.alert_drawdown_pct = alert_drawdown_pct
        self._ticks_processed = 0
        self._signals_generated = 0

    def record_tick(self, latency_ms: float):
        self.tick_latency.record(latency_ms)
        self._ticks_processed += 1
        if latency_ms > self.alert_latency_ms:
            self._alert(f"TICK_LATENCY: {latency_ms:.1f}ms > {self.alert_latency_ms}ms")

    def record_signal(self, latency_ms: float, signal_type: str):
        self.signal_latency.record(latency_ms)
        self._signals_generated += 1

    def check_drawdown(self, drawdown: float):
        if drawdown > self.alert_drawdown_pct:
            self._alert(f"DRAWDOWN: {drawdown*100:.1f}% > {self.alert_drawdown_pct*100:.0f}%")

    def check_throughput(self, ticks_per_sec: float, min_tps: float = 1000.0):
        if ticks_per_sec < min_tps:
            self._alert(f"THROUGHPUT: {ticks_per_sec:.0f} tps < {min_tps:.0f} tps min")

    def _alert(self, msg: str):
        self.alerts.append(msg)
        logger.warning("monitoring_alert", alert=msg)

    def summary(self) -> dict:
        return {
            "ticks_processed": self._ticks_processed,
            "signals_generated": self._signals_generated,
            "signal_latency_avg_ms": round(self.signal_latency.avg_ms, 3),
            "signal_latency_p95_ms": round(self.signal_latency.p95_ms, 3),
            "signal_latency_max_ms": round(self.signal_latency.max_ms, 3),
            "tick_latency_avg_ms": round(self.tick_latency.avg_ms, 3),
            "alerts": len(self.alerts),
            "recent_alerts": self.alerts[-5:] if self.alerts else [],
        }

    def print_report(self):
        s = self.summary()
        print(f"\n{'='*60}")
        print(f"  MONITORING REPORT")
        print(f"{'='*60}")
        print(f"  Ticks processed:    {s['ticks_processed']:,}")
        print(f"  Signals generated:  {s['signals_generated']}")
        print(f"  Signal latency avg: {s['signal_latency_avg_ms']:.3f} ms")
        print(f"  Signal latency p95: {s['signal_latency_p95_ms']:.3f} ms")
        print(f"  Signal latency max: {s['signal_latency_max_ms']:.3f} ms")
        print(f"  Alerts:             {s['alerts']}")
        if s['recent_alerts']:
            for a in s['recent_alerts']:
                print(f"    ⚠ {a}")
        print(f"{'='*60}\n")
