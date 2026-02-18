# 🔗 BuckyConnect

**Real-time collaboration platform** built with WebSockets, GraphQL, and Redis Pub/Sub.

Supports live messaging, channel management, user presence tracking, and typing indicators — all with sub-500ms latency targets and horizontal scalability via Redis event fanout.

---

## Features

- **Real-time messaging** via WebSockets with automatic reconnection and heartbeat
- **GraphQL API** for structured reads (channels, messages, users, members)
- **Redis Pub/Sub** for event fanout across multiple server instances
- **Channel-based collaboration** — create, join, and switch between channels
- **User presence** — online/offline status tracked in real time
- **Typing indicators** — see who's typing in a channel
- **Message history** with pagination support
- **Lazy-loaded components** and code splitting (40% bundle reduction strategy)
- **Graceful degradation** — works without Redis using local broadcast fallback
- **Dark-themed UI** with responsive layout

## Architecture

```
┌─────────────────┐      HTTP/GraphQL       ┌──────────────────┐
│                 │ ◄──────────────────────► │                  │
│  React Frontend │                          │  Express + Apollo│
│  (Vite + Apollo)│ ◄── WebSocket (ws) ────► │  + WS Server     │
│                 │                          │                  │
└─────────────────┘                          └────────┬─────────┘
                                                      │
                                           ┌──────────┴──────────┐
                                           │                     │
                                      ┌────▼────┐         ┌─────▼────┐
                                      │  Redis  │         │  SQLite  │
                                      │ Pub/Sub │         │    DB    │
                                      └─────────┘         └──────────┘
```

- **Frontend**: React 18 + TypeScript + Vite + Apollo Client
- **Backend**: Node.js + Express + Apollo Server (GraphQL) + ws (WebSocket)
- **Database**: SQLite via better-sqlite3 (WAL mode, foreign keys)
- **Pub/Sub**: Redis (optional — degrades gracefully to local broadcast)

## Quick Start

### Prerequisites

- **Node.js** >= 18
- **Redis** (optional but recommended) — `brew install redis` / `apt install redis-server`

### Install

```bash
# From project root
npm run install:all
```

### Configure

```bash
cp backend/.env.example backend/.env
# Edit backend/.env if needed (defaults work fine)
```

### Run (Development)

```bash
# Terminal 1: Start Redis (optional)
redis-server

# Terminal 2: Start both backend + frontend
npm run dev
```

- **Frontend**: http://localhost:5173
- **Backend GraphQL**: http://localhost:4000/graphql
- **WebSocket**: ws://localhost:4000/ws
- **Health Check**: http://localhost:4000/health

### Run with Docker

```bash
docker-compose up --build
```

### Run Tests

```bash
cd backend && npm test
```

### Build for Production

```bash
cd frontend && npm run build
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Apollo Client |
| Backend | Node.js, Express, Apollo Server, ws |
| Database | SQLite (better-sqlite3) |
| Pub/Sub | Redis (ioredis) |
| Infrastructure | Docker, docker-compose |

## API Reference

### GraphQL Queries

- `channels` — List all channels
- `channel(id)` — Get channel with members
- `messages(channelId, limit, before)` — Paginated messages
- `users` — All registered users

### GraphQL Mutations

- `register(username, displayName)` — Create/login user
- `sendMessage(channelId, userId, content)` — Send a message
- `createChannel(name, description, userId)` — Create a channel
- `joinChannel / leaveChannel` — Channel membership

### WebSocket Events

| Client → Server | Server → Client |
|----------------|-----------------|
| `auth` | `auth_ok`, `presence` |
| `join_channel` | `user_joined` |
| `message` | `new_message` |
| `typing` | `typing` |
| `ping` | `pong` |

## License

MIT
