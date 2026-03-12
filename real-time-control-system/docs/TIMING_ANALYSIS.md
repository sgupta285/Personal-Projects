# Timing Analysis

## Goal

Measure whether the control loop can hold a stable 10 ms cadence while sensing and filtering continue in parallel.

## What is logged

Each control iteration logs:

- target setpoint
- true plant speed
- raw and filtered measurements
- control output
- instantaneous error
- loop jitter in milliseconds
- sensor delay in milliseconds
- whether the loop overran its period

## Interpretation

- low absolute jitter indicates the controller work is lightweight enough for the configured schedule
- overrun counts matter more than average jitter because they indicate missed timing budgets
- sensor delay should be reviewed together with tracking error because stale measurements directly affect phase lag

## Caveat

This repository measures userspace timing on Linux. It is good for deterministic engineering habits and instrumentation, but it should not be presented as a substitute for a true hard real-time validation environment.
