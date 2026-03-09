import json
import logging

try:
    from kafka import KafkaProducer
except Exception:  # pragma: no cover
    KafkaProducer = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(self) -> None:
        self._producer = None
        if KafkaProducer is None:
            logger.warning("kafka-python is not installed; event publishing is disabled.")
            return
        try:
            self._producer = KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
                retries=3,
            )
        except Exception as exc:
            logger.warning("Kafka producer unavailable: %s", exc)

    def publish(self, topic: str, payload: dict) -> bool:
        if not self._producer:
            logger.info("Skipping Kafka publish to %s because producer is unavailable.", topic)
            return False
        try:
            self._producer.send(topic, payload)
            self._producer.flush(timeout=5)
            return True
        except Exception as exc:
            logger.warning("Failed to publish event to %s: %s", topic, exc)
            return False


publisher = EventPublisher()
