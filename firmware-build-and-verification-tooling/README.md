# Firmware Build and Verification Tooling

Firmware teams usually do not fail because they cannot compile code. They fail because releases drift, build outputs are hard to compare, validation is spread across ad hoc shell history, and debugging a bad package takes longer than it should. This repository is a compact but production-minded version of the tooling layer around a device firmware release process.

It is built around the README-backed project scope: deterministic artifacts, scripted validation, command-line automation, reproducible packaging, debug-friendly verification, and a realistic hardware-software integration step. The implementation uses a small C firmware sample, Python orchestration, Bash workflow wrappers, Make-based native builds, Docker for environment consistency, and CI for release discipline.

## What is in this repo

- A small C firmware sample split into **bootloader** and **application** components
- A **Make** build that emits ELF and raw binary artifacts
- A Python CLI called **fwtool** for build, package, verify, hardware-integration, and clean operations
- Deterministic release packaging with fixed timestamps and stable manifest generation
- A device simulator that acts like a lightweight hardware-integration checkpoint
- Bash scripts for bootstrap, verification, and simple benchmark runs
- Docker and GitHub Actions support so the workflow is repeatable outside a single laptop

## Source-backed project goals

From the attached portfolio README, this project is framed around build tooling, verification, command-line automation, release engineering, testing, and hardware-software integration. The explicit outcomes are better release consistency, easier root-cause analysis, and faster build times through incremental compilation and caching.

That translates here into five concrete goals:

1. **Reproducible output**: release bundles should be deterministic when source inputs do not change.
2. **Scripted verification**: build validation should be runnable from one command.
3. **Debuggability**: manifests, checksums, and metadata should make bad releases easier to inspect.
4. **Hardware-aware validation**: a release should survive a device-facing sanity check before promotion.
5. **Incremental operation**: unchanged builds should reuse prior results and surface cache hits clearly.

## Architecture

```text
C firmware sources
  ├─ src/bootloader/main.c
  └─ src/app/main.c
        │
        ▼
      Make
        │
        ├─ build/<board>/bin/*.elf
        ├─ build/<board>/bin/*.bin
        └─ build/<board>/manifest.json
        │
        ▼
   Python fwtool CLI
        ├─ build
        ├─ package
        ├─ verify
        └─ hil
        │
        ▼
 deterministic release bundle in dist/
        │
        └─ optional hardware handshake through the device simulator
```

## Repository layout

```text
firmware-build-and-verification-tooling/
├── config/
│   └── demo_board.json
├── docs/
│   └── release_flow.md
├── include/
│   └── common.h
├── scripts/
│   ├── benchmark.sh
│   ├── bootstrap.sh
│   └── verify.sh
├── src/
│   ├── app/
│   │   └── main.c
│   └── bootloader/
│       └── main.c
├── tools/fwtool/
│   ├── fwtool/
│   │   ├── build.py
│   │   ├── cli.py
│   │   ├── device_sim.py
│   │   ├── package.py
│   │   ├── utils.py
│   │   └── verify.py
│   └── tests/
│       └── test_fwtool.py
├── .github/workflows/ci.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── requirements-dev.txt
```

## Core workflow

### 1. Build

The build step compiles the bootloader and application, emits `.elf` and `.bin` artifacts, and writes a manifest with board, version, size, and checksum metadata.

```bash
export PYTHONPATH=$(pwd)/tools/fwtool
python -m fwtool.cli build --version 1.0.0
```

Example output:

```json
{
  "board": "demo-board",
  "version": "1.0.0",
  "manifest": "/path/to/build/demo-board/manifest.json",
  "cache_hit": false
}
```

### 2. Package

The package step creates a deterministic release tarball and a detached checksum file.

```bash
python -m fwtool.cli package --version 1.0.0
```

Artifacts end up in `dist/`:

- `firmware-demo-board-1.0.0.tar.gz`
- `firmware-demo-board-1.0.0.sha256`

### 3. Verify

The verification step opens the archive, checks manifest hashes against actual payload bytes, and returns a per-component pass/fail summary.

```bash
python -m fwtool.cli verify dist/firmware-demo-board-1.0.0.tar.gz
```

### 4. Hardware integration checkpoint

The `hil` command starts a small TCP device simulator, creates a release, verifies it, and sends a board-aware validation payload over the wire.

```bash
python -m fwtool.cli hil --version 1.0.0 --port 9107
```

That is obviously lighter than real board flashing, but it preserves the operational idea from the project description: a build is not done when it compiles, it is done when it survives an integration-facing validation step.

## Local setup

### Option A: Python virtual environment

```bash
./scripts/bootstrap.sh
source .venv/bin/activate
export PYTHONPATH=$(pwd)/tools/fwtool
```

### Option B: direct install

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
export PYTHONPATH=$(pwd)/tools/fwtool
```

### System requirements

- Python 3.10+
- `gcc`
- `make`
- `objcopy` from binutils

## Useful commands

### Clean previous outputs

```bash
python -m fwtool.cli clean
```

### Run the full verification path

```bash
./scripts/verify.sh 1.1.0
```

### Measure caching behavior

```bash
./scripts/benchmark.sh
```

## Deterministic packaging notes

The release archive is produced with:

- fixed file timestamps
- stable JSON serialization
- explicit ownership metadata in tar members
- consistent archive contents and naming

That means if the source tree, build flags, board configuration, and version are unchanged, the resulting release structure is stable and easy to compare across environments.

## Incremental build and caching

The build helper computes a fingerprint over:

- board config
- firmware version
- C source files
- public headers

If that fingerprint matches the last recorded build index and expected binaries are present, the tool reports `cache_hit: true`. This is a simple stand-in for a more advanced build cache, but it maps cleanly to the project goal of reducing build time through incremental work reuse.

## Testing

Run the unit and integration tests with:

```bash
pytest
```

The tests cover:

- build manifest generation
- deterministic packaging and archive verification
- a full device simulator round trip

## Docker

Build the container:

```bash
docker build -t fwtooling .
```

Run the integration path inside Docker:

```bash
docker run --rm fwtooling
```

## CI

The GitHub Actions workflow installs native build tooling, installs the Python package, runs the test suite, and executes the verification smoke path.

That keeps the repo aligned with the project’s release-engineering and testing emphasis rather than leaving validation as a manual step.

## Design decisions

### Why keep the firmware sample small?

Because the point of this repo is the tooling around the firmware lifecycle, not the embedded application logic itself. A small native target makes the build, packaging, and verification paths easier to inspect and reproduce.

### Why use both Python and Bash?

Python is better for structured manifests, packaging, and verification logic. Bash is still useful for one-command operational workflows like environment setup and smoke checks. That split matches how release tooling often evolves in real teams.

### Why include a device simulator?

The source project explicitly mentions hardware-software integration. A simulator is the lightest way to make that part concrete in a repo that still runs on a developer workstation and in CI.

## Limitations

- The firmware sample targets the host compiler rather than a real MCU cross-compiler.
- The hardware integration check is a simulator handshake, not a board flash-and-readback cycle.
- The cache is content-based and local, not distributed.
- Verification checks package integrity and metadata consistency, not deep runtime correctness on real hardware.

## Reproducibility notes

- The build metadata is written to `build/<board>/manifest.json`.
- The release bundle in `dist/` includes both a manifest and a verification payload.
- The checksum sidecar makes it easy to compare release outputs in automation.
- The CI job exercises the same top-level verification flow a local engineer would run.
