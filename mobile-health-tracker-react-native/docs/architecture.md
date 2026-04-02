# Architecture notes

PulseLog is structured around a mobile-first local data path.

1. UI interactions create workout, meal, or goal records.
2. Records are written to local SQLite immediately.
3. Redux state is updated from the same payload so the UI stays responsive.
4. A sync queue records the change for eventual upload.
5. A remote adapter flushes the queue when the user manually syncs or when a background trigger is wired in.
6. Health provider adapters fetch daily activity snapshots from either demo mode, HealthKit, or Google Fit.

This keeps the happy path reliable even without connectivity.
