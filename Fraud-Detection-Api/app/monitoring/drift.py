"""
Data drift monitoring using Population Stability Index (PSI).
Tracks prediction score distributions over sliding windows and fires
retraining alerts when drift exceeds thresholds.
"""

import time
import threading
import numpy as np
import structlog
from collections import deque

from app.config import settings

logger = structlog.get_logger()


def compute_psi(reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
    """
    Compute Population Stability Index between two distributions.
    PSI < 0.1: no significant change
    PSI 0.1-0.2: moderate shift
    PSI > 0.2: significant drift → retrain
    """
    eps = 1e-6
    breakpoints = np.linspace(0, 1, bins + 1)

    ref_counts = np.histogram(reference, bins=breakpoints)[0].astype(float) + eps
    cur_counts = np.histogram(current, bins=breakpoints)[0].astype(float) + eps

    ref_pct = ref_counts / ref_counts.sum()
    cur_pct = cur_counts / cur_counts.sum()

    psi = np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct))
    return float(psi)


class DriftMonitor:
    def __init__(self, window_size: int = settings.drift_window_size):
        self._window_size = window_size
        self._reference_scores: np.ndarray | None = None
        self._current_window: deque = deque(maxlen=window_size)
        self._psi_history: list[dict] = []
        self._alert_active = False
        self._total_predictions = 0
        self._fraud_count = 0
        self._lock = threading.Lock()
        self._last_check_time = time.time()

    def set_reference(self, scores: list[float]):
        """Set the reference (training) distribution."""
        self._reference_scores = np.array(scores)
        logger.info("drift_reference_set", n_samples=len(scores))

    def record_prediction(self, fraud_score: float, is_fraud: bool):
        """Record a new prediction score for drift tracking."""
        with self._lock:
            self._current_window.append(fraud_score)
            self._total_predictions += 1
            if is_fraud:
                self._fraud_count += 1

    def check_drift(self) -> dict | None:
        """
        Check for distribution drift against reference.
        Returns drift report if window is full, None otherwise.
        """
        with self._lock:
            if self._reference_scores is None:
                return None
            if len(self._current_window) < self._window_size:
                return None

            current = np.array(self._current_window)
            psi = compute_psi(self._reference_scores, current)

            report = {
                "psi": round(psi, 6),
                "threshold": settings.drift_psi_threshold,
                "drift_detected": psi > settings.drift_psi_threshold,
                "window_size": len(current),
                "current_mean": round(float(current.mean()), 6),
                "current_std": round(float(current.std()), 6),
                "reference_mean": round(float(self._reference_scores.mean()), 6),
                "reference_std": round(float(self._reference_scores.std()), 6),
                "timestamp": time.time(),
            }

            self._psi_history.append(report)
            if len(self._psi_history) > 100:
                self._psi_history = self._psi_history[-100:]

            if report["drift_detected"] and not self._alert_active:
                self._alert_active = True
                logger.warning(
                    "drift_alert",
                    psi=report["psi"],
                    threshold=report["threshold"],
                    action="retrain_recommended",
                )
            elif not report["drift_detected"] and self._alert_active:
                self._alert_active = False
                logger.info("drift_alert_cleared", psi=report["psi"])

            self._last_check_time = time.time()
            return report

    def get_status(self) -> dict:
        fraud_rate = (self._fraud_count / self._total_predictions * 100) if self._total_predictions > 0 else 0.0
        latest_psi = self._psi_history[-1] if self._psi_history else None

        return {
            "total_predictions": self._total_predictions,
            "fraud_count": self._fraud_count,
            "fraud_rate_pct": round(fraud_rate, 4),
            "window_fill": len(self._current_window),
            "window_size": self._window_size,
            "alert_active": self._alert_active,
            "latest_psi": latest_psi,
            "psi_history_length": len(self._psi_history),
        }

    def generate_reference_from_uniform(self, n_samples: int = 5000):
        """
        Generate a synthetic reference distribution for initial deployment.
        In production, this would be computed from the training set predictions.
        """
        np.random.seed(42)
        # Simulate typical fraud score distribution: most near 0, few near 1
        scores = np.concatenate([
            np.random.beta(1, 20, size=int(n_samples * 0.98)),  # legitimate
            np.random.beta(8, 2, size=int(n_samples * 0.02)),   # fraudulent
        ])
        self.set_reference(scores.tolist())


drift_monitor = DriftMonitor()
