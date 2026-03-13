# Operations Notes

## Build

```bash
make build
```

## Run a scenario

```bash
./build/daq_acquire --scenario baseline
```

## Replay a stream

```bash
./build/daq_replay --input data/generated/baseline_stream.bin --max-messages 20
```

## Common files

- `*_stream.bin`: binary stream written by the acquisition service
- `*_metrics.csv`: interval metrics
- `*_summary.json`: run-level summary
- `*_metrics.prom`: Prometheus-style text export
- `*_replay_summary.json`: replay-level validation summary

## Troubleshooting

### No output files generated
Make sure the `data/generated/` directory exists and the build completed successfully.

### Test failures
Run `make test` to rebuild and run both the queue and metrics tests from a clean build directory.

### Very high drop rate
Lower the rate or number of sources, or reduce `writer_sleep_ms` in the selected scenario.

### Replay shows zero records
Check that the binary path points to a generated `*_stream.bin` file and that the acquisition run completed normally.
