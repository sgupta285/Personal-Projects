# Mobile Health Tracker (React Native)

PulseLog is a cross-platform mobile health tracking app built with React Native and TypeScript. The app is centered on four jobs that matter in a real health product: logging workouts, tracking nutrition, monitoring progress against goals, and importing connected activity data from phone-level health providers. The repo is intentionally designed as an offline-first mobile codebase rather than a thin UI mockup, so local persistence, sync safety, and health-provider boundaries are treated as first-class concerns.

The scope comes directly from the uploaded portfolio README. That source describes a cross-platform mobile health tracker with workout logging, nutrition tracking, goal monitoring, smooth navigation and responsive layouts, offline-first persistence with background sync and conflict resolution, and integration with device health APIs through HealthKit and Google Fit. fileciteturn9file2

## What this repo includes

- React Native and Expo app with TypeScript and Redux Toolkit state management
- Bottom-tab navigation across dashboard, workouts, nutrition, goals, and settings
- Local SQLite persistence for workouts, meals, and goals
- Offline-first logging flow that writes locally before remote sync
- Sync queue with conflict-resolution utility and mock remote adapter for local verification
- Health provider abstraction for demo mode, HealthKit, and Google Fit connectors
- Seeded demo data so the app is usable on first run
- Unit tests for reducers and sync conflict handling
- Detailed architecture notes and practical setup instructions

## Real-world framing

Health and fitness apps usually feel simple at the surface, but they become fragile quickly if they assume perfect connectivity or full access to device-specific native APIs. A user expects to log a workout in the gym basement with no signal, see their data immediately, and trust that the app will catch up later. They also expect platform integrations to work when available without making the entire product unusable when permissions are denied.

That is the tradeoff this repo tries to model. The app has a real local data path, queued sync behavior, and clean adapter boundaries around health integrations. In other words, it is built to behave like a practical mobile product rather than a demo that only works under perfect conditions.

## README-backed design goals

From the source README, this project should show: cross-platform React Native development, intuitive navigation and mobile UI, offline-first persistence, background sync and conflict resolution concepts, and integration points for HealthKit and Google Fit. The design here reflects those exact expectations while keeping the repository runnable in local development through a demo health provider and a mock sync target. fileciteturn9file2

## Architecture

```text
React Native screens
  |- Dashboard
  |- Workouts
  |- Nutrition
  |- Goals
  |- Settings
        |
        v
Redux Toolkit store
  |- workouts slice
  |- nutrition slice
  |- goals slice
  |- sync queue slice
  |- activity snapshot slice
        |
        +--> SQLite persistence layer
        +--> sync service and remote adapter
        +--> health provider adapters
```

## Key product flows

### 1. Log a workout offline

1. User taps Quick add workout.
2. The workout is written to SQLite immediately.
3. Redux state updates in the same interaction.
4. A sync item is appended to the local queue.
5. The change remains visible even without connectivity.

### 2. Import connected health activity

1. The app resolves a provider based on environment configuration.
2. Demo mode returns seeded activity data for local runs.
3. Native provider adapters are kept behind the same interface so HealthKit and Google Fit wiring can be added without changing screen code.

### 3. Resolve sync conflicts

1. Both local and remote payloads carry update timestamps.
2. The conflict resolution utility prefers the latest write.
3. The chosen record becomes the source of truth for the next sync cycle.

## Folder structure

```text
mobile-health-tracker-react-native/
├── src/
│   ├── components/
│   ├── database/
│   ├── hooks/
│   ├── navigation/
│   ├── screens/
│   ├── services/
│   ├── store/
│   ├── types/
│   └── utils/
├── docs/
├── scripts/
├── tests/
├── App.tsx
├── app.json
├── package.json
└── .env.example
```

## Tech stack

This repository stays aligned with the README stack:

- React Native
- TypeScript
- Redux Toolkit
- SQLite via `expo-sqlite`
- HealthKit and Google Fit adapter boundaries

## Local setup

### 1. Install dependencies

```bash
npm install
```

### 2. Copy environment variables

```bash
cp .env.example .env
```

### 3. Start the app

```bash
npm run start
```

Then open the app in an iOS simulator, Android emulator, or Expo Go.

## Environment variables

| Variable | Purpose |
|---|---|
| `EXPO_PUBLIC_APP_MODE` | Controls demo-mode assumptions for local development |
| `EXPO_PUBLIC_SYNC_ENDPOINT` | Placeholder remote sync target |
| `EXPO_PUBLIC_HEALTH_PROVIDER` | `demo`, `healthkit`, or `google_fit` |
| `EXPO_PUBLIC_ENABLE_DEMO_SEED` | Seeds local SQLite on first run |

## Screens

### Dashboard

Shows high-level activity, workout volume, calorie intake, goal progress, and sync health.

### Workouts

Displays the workout log and includes a quick-add flow for demo verification.

### Nutrition

Tracks meals and macro estimates with local persistence.

### Goals

Monitors goal progress with simple progress visualizations.

### Settings

Shows health-provider mode and allows a manual sync against the mock remote adapter.

## Data model notes

### Workouts

- type
- duration
- calories burned
- notes
- date
- update timestamp
- sync status

### Meals

- meal type
- calories
- protein, carbs, fat
- date
- update timestamp
- sync status

### Goals

- title
- target
- unit
- progress
- optional deadline
- update timestamp
- sync status

## Sync and offline design

The most important engineering choice in this repo is that local writes happen before remote writes. That keeps the UI responsive and resilient. The sync queue then carries the eventual consistency burden. In a production mobile system I would likely add connectivity-awareness, retry backoff, background tasks, and encrypted local storage for sensitive records. Here, the repo keeps the design honest without overbuilding beyond the README.

## Health provider integration notes

This repository intentionally keeps HealthKit and Google Fit behind adapter interfaces. The shipped implementation defaults to demo mode because a GitHub-ready repo should still run on a fresh machine without requiring native entitlement setup, developer certificates, or live health permissions.

That said, the integration boundary is already present:

- `resolveHealthProvider()` chooses the active connector
- `HealthProvider` defines a stable interface for activity snapshots
- `HealthKitProvider` and `GoogleFitProvider` can be expanded into native modules later without affecting screen code

## Running tests

```bash
npm test
```

## Useful demo flow

1. Launch the app.
2. Review the seeded dashboard metrics.
3. Add a workout from the Workouts tab.
4. Add a meal from the Nutrition tab.
5. Add a goal from the Goals tab.
6. Open Settings and run a manual sync.
7. Return to the dashboard to confirm the queue is cleared.

## Design decisions

### Why Expo instead of bare React Native

Expo keeps the repo easier to run and review while still supporting the architectural patterns that matter here.

### Why SQLite instead of pure Redux persistence

The README explicitly calls for offline-first behavior and local persistence. SQLite makes that requirement real.

### Why a mock remote service

A mobile repo should be runnable out of the box. The mock remote adapter keeps the sync path demonstrable without pulling in a second backend repository that the README never asked for.

### Why adapter boundaries for health APIs

Native health integrations are platform-specific and permission-heavy. The interface keeps the app stable whether those integrations are live, incomplete, or unavailable.


