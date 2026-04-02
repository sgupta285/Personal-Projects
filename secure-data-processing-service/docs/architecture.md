# Architecture Notes

The service is structured around four security boundaries.

1. Identity and session issuance.
2. Policy enforcement for rows and columns.
3. Envelope encryption and key lifecycle.
4. Immutable audit and evidence generation.

For local runs, AWS KMS and Secrets Manager are represented by file-backed providers with the same interface surface so the rest of the service can be exercised end to end.
