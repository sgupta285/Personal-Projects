import json
import logging
import time

try:
    from kafka import KafkaConsumer, KafkaProducer
except Exception:  # pragma: no cover
    KafkaConsumer = None
    KafkaProducer = None

from app.core.config import settings
from worker.db_ops import apply_moderation_result
from worker.engine import moderate

logger = logging.getLogger(__name__)


def _build_consumer():
    if KafkaConsumer is None:
        raise RuntimeError("kafka-python is not installed.")
    return KafkaConsumer(
        settings.kafka_ads_submitted_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="ads-integrity-worker",
    )


def _build_producer():
    if KafkaProducer is None:
        return None
    return KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        retries=3,
    )


def run_consumer_forever() -> None:
    producer = None
    while True:
        try:
            consumer = _build_consumer()
            producer = _build_producer()
            logger.info("Moderation worker connected to Kafka at %s", settings.kafka_bootstrap_servers)
            break
        except Exception as exc:
            logger.warning("Kafka not ready yet: %s", exc)
            time.sleep(5)

    for message in consumer:
        payload = message.value
        ad_id = payload["ad_id"]

        result = moderate(payload).to_dict()
        apply_moderation_result(ad_id, result)

        if producer:
            try:
                producer.send(
                    settings.kafka_ads_moderated_topic,
                    {
                        "ad_id": ad_id,
                        "decision": result["decision"],
                        "risk_score": result["risk_score"],
                        "policy_hits": result["policy_hits"],
                    },
                )
                producer.flush(timeout=5)
            except Exception as exc:
                logger.warning("Failed to publish moderated event for %s: %s", ad_id, exc)

        logger.info(
            "Moderated ad=%s decision=%s risk=%.3f hits=%s",
            ad_id,
            result["decision"],
            result["risk_score"],
            ",".join(result["policy_hits"]),
        )
