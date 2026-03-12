# Real-Time Control System

A simulation-first control systems project that stabilizes motor speed under noisy sensing, delayed measurements, and concurrent data flow. The repository focuses on deterministic timing, bounded control behavior, loop jitter measurement, and a clean analysis path for reviewing stability metrics.

## What this project demonstrates

- fixed-interval control loop running at 100 Hz
- simulated motor plant with disturbance injection
- sensor thread with Gaussian noise and bounded delay
- producer/consumer pipeline between sensing and control
- moving-average and 1D Kalman filtering options
- PID controller with anti-windup and output clamping
- jitter and overrun logging for timing analysis
- Python plots for setpoint tracking, settling behavior, and loop timing

## Architecture

```text
Setpoint profile --> Controller thread --> Simulated motor plant --> Sensor thread
       ^                    |                       |                   |
       |                    |                       v                   v
       |                    +---- timing logs   state update       delayed noisy samples
       |                                                                   |
       +----------------------- analysis + replay <-------------------------+
```

The controller consumes the latest available sensor sample through a lock-protected shared state. This mirrors a common embedded pattern where the controller must make progress on schedule even if sensing is slightly delayed.

## Simulation scenario

The default workload simulates motor speed control with:

- 10 ms control period
- 12 second run time
- step changes in target speed
- transient disturbance between 6.0s and 7.0s
- configurable noise, delay, and filtering

## Build

```bash
cmake -S . -B build
cmake --build build
```

## Run the simulator

```bash
./build/realtime_control --config examples/config/default.json --output data/logs/run.csv
```

## Run tests

```bash
ctest --test-dir build --output-on-failure
```

## Generate analysis plots

```bash
python3 scripts/analyze_results.py --input data/logs/run.csv --output-dir docs/generated
```

## Generated artifacts

The packaged zip already includes:

- `data/logs/run.csv`
- `data/logs/summary.json`
- `docs/generated/control_response.png`
- `docs/generated/jitter_histogram.png`
- `docs/generated/timing_table.csv`

## Repo layout

```text
real-time-control-system/
├── CMakeLists.txt
├── Makefile
├── README.md
├── examples/config/
├── include/realtime/
├── src/
├── tests/
├── scripts/
├── data/logs/
└── docs/
```

## Notes

This is intentionally simulation-first. The abstractions are designed so the sensor and actuator layers can be replaced with hardware bindings later without rewriting the control, logging, or analysis pipeline.
