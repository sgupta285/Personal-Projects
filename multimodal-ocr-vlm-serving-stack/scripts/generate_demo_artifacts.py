import json
from pathlib import Path

artifact_dir = Path('artifacts')
artifact_dir.mkdir(exist_ok=True)
summary = {
    'stack': 'multimodal-ocr-vlm-serving-stack',
    'notes': [
        'Queue-backed job execution',
        'Memory-aware batch scheduling',
        'Prometheus metrics endpoint',
        'Helm and Kubernetes deployment scaffolding',
    ],
}
(artifact_dir / 'demo_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print('Wrote artifacts/demo_summary.json')
