# API Examples

## Load bundled benchmarks

```bash
curl -X POST http://localhost:8000/benchmarks/load-defaults
```

## Create a run

```bash
curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{
    "benchmark_id": "compare_pricing_plans_v1",
    "model_name": "demo-agent-v1",
    "prompt_version": "p1",
    "inputs": {"question": "Compare the pro and enterprise plans."},
    "final_output": {"recommendation": "enterprise", "reason": "better admin controls"},
    "trajectory": [
      {
        "step_index": 1,
        "tool_name": "knowledge_lookup",
        "action": "Read pricing docs",
        "observation": "Enterprise includes SSO",
        "latency_ms": 310,
        "success": true
      }
    ],
    "total_latency_ms": 1210,
    "estimated_cost_usd": 0.03
  }'
```

## Evaluate a run

```bash
curl -X POST http://localhost:8000/runs/<run-id>/evaluate
```

## Analyze failure mode for a run

```bash
curl -X POST http://localhost:8000/runs/<run-id>/analyze
```

## Generate a demo run for a benchmark

```bash
curl -X POST http://localhost:8000/runs/demo/browser_export_report_v1?mode=success
```

## Summary report

```bash
curl http://localhost:8000/reports/summary
```
