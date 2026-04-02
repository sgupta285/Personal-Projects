# Integration Guide

## Authentication Options

The platform supports three authentication modes:

1. `X-API-Key` for partner applications.
2. `Authorization: Bearer <token>` for OAuth-style user access tokens.
3. `Authorization: Bearer <token>` with `token_type=service` claims for service-to-service traffic.

## Versioning

Versioning is path-based.

- `/api/v1/...` keeps a compact response shape.
- `/api/v2/...` adds richer metadata, idempotency support, and cursor pagination.

## Retry Guidance

- Safe to retry `GET` requests.
- `POST /api/v2/orders` supports `Idempotency-Key`.
- Respect `429` responses and read `Retry-After`.

## Error Contract

Errors return JSON in the following form:

```json
{
  "error": {
    "code": "quota_exceeded",
    "message": "Daily quota exceeded",
    "request_id": "..."
  }
}
```
