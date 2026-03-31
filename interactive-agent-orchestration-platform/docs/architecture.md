# Architecture Notes

This project splits orchestration into four concerns:

1. **Control plane API**
   Handles run creation, retrieval, intervention recording, and execution triggers.

2. **Realtime event service**
   Streams step-by-step progress to the operator UI so the user can follow a run without polling.

3. **Worker process**
   Consumes queued runs and executes them using the shared orchestration engine.

4. **Operator UI**
   Displays live status, run history, step traces, latency, cost, and intervention controls.

## Why the shared core package exists

The most important logic in this repository is not the HTTP routing. It is the execution model:

- what a run looks like
- how step traces are recorded
- how interventions mutate state
- how cost and latency are accumulated
- how a run can be replayed or resumed

Keeping that logic in `packages/core` makes it easier to test and reuse across the API, worker, and realtime services.

## Event model

The shared engine emits structured events for:

- run creation
- run start and completion
- step start and completion
- failures
- operator interventions
- cost updates

The UI can subscribe to those events through the realtime service and reconstruct execution state without waiting for periodic refreshes.
