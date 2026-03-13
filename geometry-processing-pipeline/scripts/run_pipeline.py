from __future__ import annotations

import argparse
from pathlib import Path
import json

from geometry_pipeline.io import load_mesh, save_obj
from geometry_pipeline.pipeline import process_mesh


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--voxel-size', type=float, default=0.25)
    parser.add_argument('--layer-height', type=float, default=0.2)
    args = parser.parse_args()

    mesh = load_mesh(args.input)
    result = process_mesh(mesh, voxel_size=args.voxel_size, layer_height=args.layer_height)

    out_dir = Path('data/output')
    out_dir.mkdir(parents=True, exist_ok=True)
    save_obj(result.cleaned, out_dir / f'{args.name}_cleaned.obj')
    save_obj(result.simplified, out_dir / f'{args.name}_simplified.obj')
    (out_dir / f'{args.name}_slices.json').write_text(json.dumps(result.slices, indent=2))
    (out_dir / f'{args.name}_summary.json').write_text(json.dumps({
        'timings': result.timings,
        'validations': result.validations,
        'slice_layers': len(result.slices),
    }, indent=2))
    print(f'Pipeline finished for {args.name}')


if __name__ == '__main__':
    main()
