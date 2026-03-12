# Findings

## Overview

This project implements a simulation-first real-time motor speed controller with deterministic update intervals, sensor delay, filtering, and timing instrumentation. The main goal is to show systems-level thinking around predictability and reliability rather than to chase perfect physical realism.

## Architecture

- a fixed-rate controller thread runs at 100 Hz
- a sensor thread produces delayed and noisy measurements
- the plant is updated by the controller on the same deterministic cadence
- filtering is applied before the measurement reaches the PID loop
- jitter, delay, overrun, and response logs are written to CSV for analysis

## Methodology

The simulation uses a first-order motor model, step changes in target speed, and a negative disturbance event midway through the run. The controller uses PID with integral clamping and output saturation. The sensor path supports a simple moving average and a 1D Kalman filter. Timing jitter is derived from the observed work duration of each control cycle relative to the configured 10 ms period.

## Results

The packaged run shows stable tracking after each setpoint transition, bounded overshoot, and low control-loop jitter on a normal Linux userspace process. The sensor delay adds some lag, but the filtered signal remains stable enough for the controller to recover after the disturbance window.

Key generated artifacts in this repo:

- `data/logs/run.csv`
- `data/logs/summary.json`
- `docs/generated/control_response.png`
- `docs/generated/jitter_histogram.png`
- `docs/generated/timing_table.csv`

## Limitations

- timing is best-effort userspace timing, not a hard RTOS guarantee
- the plant model is intentionally simple and single-axis
- concurrency uses mutex-protected shared state instead of a lock-free queue
- no hardware drivers are included in this simulation-first version

## Practical extensions

- swap the simulated plant for a hardware abstraction layer
- replace the shared sample slot with a bounded ring buffer
- add a state observer for more aggressive disturbance rejection
- move timing to PREEMPT_RT or an RTOS-backed target for tighter guarantees
