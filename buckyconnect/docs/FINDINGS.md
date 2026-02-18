# BuckyConnect — Project Findings Report

## 1. Overview

BuckyConnect is a real-time collaboration platform designed to support high-concurrency messaging with structured data access. It combines WebSockets for live event delivery, GraphQL for efficient reads, and Redis Pub/Sub for horizontal event fanout across server instances.

The platform enables users to create channels, exchange messages in real time, track presence, and see typing indicators — all within a polished, dark-themed web interface.

## 2. Problem Statement

Modern collaboration tools require instantaneous feedback (message delivery, presence, typing indicators) while also serving structured data efficiently (message history, user profiles, channel metadata). A naive REST-only approach introduces excessive polling and latency, while a WebSocket-only approach makes structured queries cumbersome.

BuckyConnect solves this by separating concerns: **GraphQL handles reads** (channel lists, message history, member lookups) while **WebSockets handle real-time events** (new messages, typing, presence changes). Redis Pub/Sub enables multi-instance deployments where an event published on one server is delivered to clients connected to any server.

## 3. Key Design Choices & Tradeoffs

### Dual Protocol (GraphQL + WebSocket)
- **Choice**: Use GraphQL for initial data loading and paginated reads; WebSockets for live event streaming.
- **Tradeoff**: Added complexity of two communication layers vs. a single protocol, but each protocol is used where it excels.
- **Benefit**: GraphQL's query flexibility avoids over/under-fetching for reads; WebSockets provide sub-100ms delivery for events.

### Redis Pub/Sub for Fanout
- **Choice**: Redis as the event bus between server instances.
- **Tradeoff**: Adds an infrastructure dependency, but the system degrades gracefully to local-only broadcast when Redis is unavailable.
- **Benefit**: Enables horizontal scaling — any instance can publish events that reach clients on all instances.

### SQLite for Persistence
- **Choice**: SQLite (WAL mode) instead of PostgreSQL or DynamoDB for local development.
- **Tradeoff**: Limited write concurrency and no built-in replication, but dramatically simpler setup with zero external dependencies.
- **Benefit**: Single-file database, zero configuration, excellent read performance for the expected workload.

### Lazy Loading & Code Splitting
- **Choice**: Vite's `manualChunks` for vendor/apollo splitting; React `lazy()` for the members panel.
- **Tradeoff**: Slightly more complex bundling configuration.
- **Benefit**: Smaller initial bundle, faster first paint — aligned with the 40% bundle reduction target.

### Session-Based Auth (Simplified)
- **Choice**: Header-based user identification (`x-user-id`) with session storage on the client.
- **Tradeoff**: Not production-secure — suitable for demo/development only.
- **Benefit**: Eliminates OAuth/JWT complexity to focus on the core collaboration mechanics.

## 4. Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                               │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  React + Vite                                            │      │
│  │  ┌─────────────┐  ┌───────────────┐  ┌──────────────┐   │      │
│  │  │ Apollo Client│  │ useWebSocket  │  │ React Router │   │      │
│  │  │  (GraphQL)   │  │   (WS Hook)   │  │  (Lazy Load) │   │      │
│  │  └──────┬───────┘  └──────┬────────┘  └──────────────┘   │      │
│  └─────────┼─────────────────┼───────────────────────────────┘      │
│            │ HTTP             │ WebSocket                           │
└────────────┼─────────────────┼─────────────────────────────────────┘
             │                 │
┌────────────┼─────────────────┼─────────────────────────────────────┐
│            ▼                 ▼           SERVER LAYER               │
│  ┌──────────────────────────────────────────┐                      │
│  │  Express Server                          │                      │
│  │  ┌─────────────────┐  ┌──────────────┐  │                      │
│  │  │  Apollo Server   │  │  WS Server   │  │                      │
│  │  │  (GraphQL API)   │  │  (ws lib)    │  │                      │
│  │  └────────┬─────────┘  └──────┬───────┘  │                      │
│  │           │                   │           │                      │
│  │           ▼                   ▼           │                      │
│  │  ┌──────────────────────────────────┐    │                      │
│  │  │  Business Logic (Resolvers +     │    │                      │
│  │  │  Message Handlers)               │    │                      │
│  │  └──────────┬───────────────────────┘    │                      │
│  └─────────────┼────────────────────────────┘                      │
│                │                                                    │
│       ┌────────┴────────┐                                          │
│       ▼                 ▼                                          │
│  ┌──────────┐    ┌──────────┐                                      │
│  │  SQLite  │    │  Redis   │                                      │
│  │   (DB)   │    │ (Pub/Sub)│                                      │
│  └──────────┘    └──────────┘                                      │
└────────────────────────────────────────────────────────────────────┘
```

## 5. How to Run

### Prerequisites
- Node.js >= 18
- Redis (optional — system works without it)

### Steps
```bash
# 1. Install all dependencies
npm run install:all

# 2. Configure environment
cp backend/.env.example backend/.env

# 3. Start Redis (optional)
redis-server

# 4. Start development servers
npm run dev

# 5. Open http://localhost:5173 in your browser
```

### Tests
```bash
cd backend && npm test
```

## 6. Known Limitations

1. **Authentication is simplified** — no JWT/OAuth; uses session storage + header-based user ID. Not suitable for production without adding proper auth.
2. **No message encryption** — messages are stored and transmitted in plaintext.
3. **SQLite write concurrency** — under very high write load, SQLite's single-writer model could bottleneck. Production would use PostgreSQL or DynamoDB.
4. **No file uploads** — text-only messaging; no image/file attachments.
5. **No message threading** — flat channel messages only; no reply chains.
6. **No rate limiting** — malicious clients could spam WebSocket events.
7. **No E2E tests** — only unit/integration tests for the database layer.

## 7. Future Improvements

- **Production auth**: JWT tokens with refresh rotation, OAuth2 providers
- **Message threading**: Reply chains with parent message references
- **File uploads**: S3-backed attachments with presigned URLs
- **Rich text**: Markdown rendering with code highlighting
- **Notifications**: Push notifications via service workers
- **Search**: Full-text message search with SQLite FTS5 or Elasticsearch
- **Rate limiting**: Per-user WS event throttling
- **E2E testing**: Playwright or Cypress for full user flow testing
- **Horizontal scaling**: Deploy multiple instances behind a load balancer with Redis-backed session sharing
- **Observability**: OpenTelemetry instrumentation, Prometheus metrics, Grafana dashboards

## 8. Screenshots

> **[Screenshot: Login Screen]**
> _Dark-themed login card with username input and "Join" button._

> **[Screenshot: Main Chat Interface]**
> _Three-panel layout: channel sidebar (left), message area (center), members panel (right). Shows real-time messages with avatars and timestamps._

> **[Screenshot: New Channel Modal]**
> _Overlay modal with channel name and description inputs._

> **[Screenshot: Typing Indicator]**
> _Italic text below the message area showing "alice is typing..."_

---

*Report generated for BuckyConnect v1.0.0*
