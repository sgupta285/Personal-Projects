from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time

import boto3

from storageinfra.config import settings


@dataclass(slots=True)
class DelayProfile:
    base_delay_ms: float = 0.0
    pressure_threshold_bytes: int | None = None
    pressure_delay_ms: float = 0.0


class LocalObjectStore:
    def __init__(self, root_dir: Path, delay: DelayProfile | None = None) -> None:
        self.root_dir = root_dir
        self.delay = delay or DelayProfile()
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _bucket_dir(self, bucket: str) -> Path:
        path = self.root_dir / bucket
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _object_path(self, bucket: str, key: str) -> Path:
        return self._bucket_dir(bucket) / key

    def _apply_delay(self, operation: str) -> None:
        delay_ms = self.delay.base_delay_ms
        if operation == "write" and self.delay.pressure_threshold_bytes is not None:
            used = sum(path.stat().st_size for path in self.root_dir.rglob("*") if path.is_file())
            if used >= self.delay.pressure_threshold_bytes:
                delay_ms += self.delay.pressure_delay_ms
        if delay_ms:
            time.sleep(delay_ms / 1000.0)

    def put_object(self, bucket: str, key: str, body: bytes) -> None:
        self._apply_delay("write")
        path = self._object_path(bucket, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)

    def get_object(self, bucket: str, key: str) -> bytes:
        self._apply_delay("read")
        return self._object_path(bucket, key).read_bytes()

    def reset(self) -> "LocalObjectStore":
        return LocalObjectStore(self.root_dir, delay=self.delay)


class MinioObjectStore:
    def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.minio_endpoint,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            use_ssl=settings.minio_secure,
        )

    def ensure_bucket(self, bucket: str) -> None:
        existing = [item["Name"] for item in self.client.list_buckets().get("Buckets", [])]
        if bucket not in existing:
            self.client.create_bucket(Bucket=bucket)

    def put_object(self, bucket: str, key: str, body: bytes) -> None:
        self.ensure_bucket(bucket)
        self.client.put_object(Bucket=bucket, Key=key, Body=body)

    def get_object(self, bucket: str, key: str) -> bytes:
        self.ensure_bucket(bucket)
        response = self.client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()


def build_store(delay: DelayProfile | None = None):
    if settings.storage_mode == "minio":
        return MinioObjectStore()
    return LocalObjectStore(settings.store_root, delay=delay)
