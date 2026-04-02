# Habit Tracker with Social Features

A production-minded habit tracking project built from the README spec for a mobile-first product with streaks, badges, friend challenges, social accountability, and push notifications. The repo is structured as a small monorepo with a React Native app and a Node.js backend backed by PostgreSQL and Redis.

The source README described a habit tracker with social accountability, streak tracking, achievement badges, smart notification timing, a friend system, challenge creation, progress sharing, and competitive leaderboards. That is the exact shape this project follows.

## What this build includes

- **Mobile app** built with React Native and TypeScript for daily tracking, challenges, friends, badges, and profile views
- **Backend API** built with Node.js and Express for habits, challenge workflows, auth, reminders, and cached leaderboards
- **PostgreSQL schema** for users, habits, entries, friendships, challenges, participants, and device tokens
- **Redis caching** for leaderboard reads
- **Push notification adapter** that builds Firebase Cloud Messaging payloads and exposes reminder previews
- **Offline-first mobile behavior** with local token storage and an offline check-in queue
- **Seed data, tests, Docker Compose, CI, smoke script, and benchmark script**

## Why it is shaped this way

The README did not describe a giant platform with messaging, video, or enterprise admin panels. It described a focused mobile product with behavioral design and social mechanics. I kept the scope disciplined around:

- habit creation and completion
- streak calculation
- badges and achievements
- friend visibility
- social challenges
- leaderboard ranking
- notification timing based on user history

That keeps the repo believable and directly aligned to the source description.

## Repository layout

```text
habit-tracker-social-features/
├── backend/
│   ├── src/
│   │   ├── config/
│   │   ├── db/
│   │   ├── middleware/
│   │   ├── routes/
│   │   ├── services/
│   │   └── types/
│   ├── scripts/
│   └── tests/
├── mobile/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── mocks/
│   │   ├── navigation/
│   │   ├── screens/
│   │   ├── services/
│   │   └── utils/
│   └── __tests__/
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Product walkthrough

### Home screen
The home screen loads the signed-in user, their current streak, earned badges, recommended reminder time, and the list of active habits. Users can check in immediately. If the API is not reachable, the habit ID is queued locally and the UI explains that it will sync later.

### Challenges
The challenge view shows active challenges and pulls a leaderboard for the selected challenge. Ranking is determined by score first and progress second.

### Friends
The friends view gives a compact list of accepted friends. In a real product this would usually connect to richer profile previews and challenge invites, but the README did not require a full social graph editor.

### Profile
The profile screen surfaces achievements and the system-generated reminder time. That reflects the behavioral design angle in the README.

## Architecture

### Mobile app
- Expo-based React Native app
- AsyncStorage-backed persistence for auth and queued offline actions
- thin API client with fallback to seeded demo data
- local notification token registration path
- bottom-tab navigation for the main product surfaces

### Backend
- Express API with JSON auth flow
- PostgreSQL for the system of record
- Redis for leaderboard caching
- pure services for streak calculation, achievement assignment, leaderboard ranking, and reminder-time recommendation
- reminder preview endpoint that returns an FCM-style payload

### Data flow
1. User logs in from the mobile app using the seeded demo account.
2. Backend returns a signed JWT.
3. Mobile app calls `/users/me`, `/users/me/friends`, `/challenges`, and `/challenges/:id/leaderboard`.
4. When the user checks in, the app posts to `/habits/:habitId/complete`.
5. The backend records the entry and recomputes streak-based stats on subsequent reads.
6. The notification preview endpoint uses recent completion history to recommend a reminder time.
7. Leaderboard reads hit Redis first and then fall back to PostgreSQL.

## Backend API summary

### Auth
- `POST /auth/login`
  - body: `{ "email": "maya@example.com" }`

### User
- `GET /users/me`
- `GET /users/me/friends`

### Habits
- `POST /habits`
- `POST /habits/:habitId/complete`

### Challenges
- `GET /challenges`
- `POST /challenges`
- `GET /challenges/:challengeId/leaderboard`

### Notifications
- `POST /notifications/device-token`
- `GET /notifications/preview`

### Health
- `GET /health`

## Database notes

The schema covers the core product entities:
- `users`
- `habits`
- `habit_entries`
- `friendships`
- `challenges`
- `challenge_participants`
- `device_tokens`

The schema is intentionally compact. It is enough to support the workflows implied by the README without drifting into unsupported features.

## Smart reminder design

The source README called out “smart timing based on user behavior patterns.” I implemented that as a small deterministic service that:
- looks at historical completion timestamps
- finds the strongest completion hour
- recommends a reminder roughly one hour earlier
- clamps the result to the user’s quiet window

That makes the feature easy to reason about, easy to test, and practical for a repo build.

## Achievements and gamification

The source README emphasized social accountability, streak tracking, and achievement badges. I modeled that with:
- streak-derived badge milestones
- weekly completion achievements
- challenge-participation achievements

This is enough to demonstrate the gamification loop without inventing a complicated points economy that was never specified.

## Local setup

### Prerequisites
- Node.js 20+
- Docker and Docker Compose
- Expo CLI optional if you want a local phone simulator workflow

### 1. Start infrastructure
From the repo root:

```bash
cp .env.example .env
docker compose up -d postgres redis
```

### 2. Start the backend
```bash
cd backend
npm install
npm run dev
```

### 3. Start the mobile app
In a new terminal:

```bash
cd mobile
npm install
npx expo start
```

If you are running the backend on a device or emulator, point `EXPO_PUBLIC_API_BASE_URL` to a reachable host.

## Seeded demo account

Use this login payload against the backend:

```json
{ "email": "maya@example.com" }
```

The mobile app already uses that account by default.

## Environment variables

### Root
- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `FCM_SERVER_KEY`
- `API_BASE_URL`

### Mobile
- `EXPO_PUBLIC_API_BASE_URL`

## Testing

### Backend tests
```bash
cd backend
npm install
npm run test
```

### Mobile tests
```bash
cd mobile
npm install
npm run test
```

The backend tests cover:
- streak computation
- badge assignment
- reminder recommendation
- FCM payload generation

The mobile test covers:
- streak label mapping

## Smoke test

After the backend is running:

```bash
cd backend
npm run smoke
```

It will:
- log in with the seeded demo user
- fetch the profile
- print a compact summary of the returned user and streak

## Benchmark

A lightweight benchmark script is included for repeated profile fetches:

```bash
cd backend
npm run benchmark
```

This is intentionally simple. The source README talked about improved completion rates and smarter notifications, not extreme systems-level throughput. The benchmark is there to validate the common read path and give a starting point for profiling.

## Deployment notes

### Backend
- Dockerfile included
- Docker Compose for local Postgres and Redis
- CI workflow for typechecking and tests
- health endpoint for readiness checks
- Redis usage is optional at runtime, so local development still works in a degraded mode if Redis is unavailable

### Mobile
- Expo app config included
- device notification registration degrades gracefully to a demo token when native push services are not wired up in development

## Design decisions

### Why Express instead of a larger backend framework
The source README only required Node.js, PostgreSQL, Redis, and FCM. Express keeps the service understandable and avoids framework noise.

### Why a monorepo
This product is inherently split between client and API. Keeping both halves together makes the repo easier to run and easier to present on GitHub.

### Why deterministic services for streaks and reminders
Streaks, reminders, and achievements are the heart of the product. Pure functions make them easy to review, easy to test, and easy to trust.

### Why offline fallback in the mobile app
The source README explicitly mentioned push notification integration and mobile development. Mobile products need to behave sensibly when connectivity is poor, so the app stores auth state and queued check-ins locally.

## Tradeoffs

- The mobile app uses Expo-friendly notification registration rather than a full native FCM bridge configuration.
- The backend uses SQL scripts for schema setup rather than a full migration framework to keep local startup straightforward.
- The social graph is intentionally lean. The README supported friends, challenges, and leaderboards, but not a complete chat or feed system.
- The API uses a seeded email login flow for demo convenience instead of a full account creation stack.

## Reproducibility notes

- Seed SQL creates a predictable demo state
- Reminder logic is deterministic
- Leaderboard ranking is deterministic
- Tests focus on the product logic that matters most to the habit loop


