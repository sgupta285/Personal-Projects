# Architecture Notes

## Overview

The system is split into three practical layers:

1. API and workflow layer in FastAPI
2. persistence layer using SQLite and explicit repository methods
3. frontend operator console scaffold in React and TypeScript

## Why explicit repositories

For an operations-heavy platform, clear SQL is easier to review than hidden ORM behavior. This keeps duplicate detection, reporting logic, and workflow writes obvious.

## Workflow model

The invoice is the center of the system. Everything else hangs off that object:

- vendor record
- payment record
- audit events

This keeps reporting and traceability straightforward.

## Extension points

- add invoice document OCR and PDF attachment storage
- add GL coding and cost-center routing
- add role-based permissions and approval thresholds
- sync payment state with ERP or AP automation systems
