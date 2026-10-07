# TraceVision

TraceVision is an early-stage project for road-scene video intelligence, with
an emphasis on reproducible evaluation and inspectable tracking failures.

## Current state

**Phase 0 complete. Phase 1 preparation implemented; dataset acceptance blocked.**

**Implemented:** an installable Python package, version/help commands, CPU-only
file-manifest creation/verification, declared sequence/split integrity checks,
software tests, and CI for Windows and Linux. The
[dataset review](docs/data-selection.md) compares ROAD-Waymo, TUMTraf-A,
TrafficMOT, ROAD, KITTI, SVMOT and BDD100K using the same criteria.

**Not implemented:** dataset-specific acquisition/preparation, inference, tracking, evaluation,
events, multimodal explanations, an API, or a public demo. No model or dataset
has been accepted. No real development subset or frozen real-file manifest
exists. SVMOT's split/scene metadata was retrieved and checksummed; its media
and object annotations were not obtained. No accuracy or performance results
are available. Phase 1 is **not complete**.

[Local verification evidence](docs/phase1-evidence.json) records the 20 passing
CPU tests, clean installed-wheel checks, build environment, tested source
hashes and verified SVMOT metadata hashes. These are software/metadata checks,
not detection or tracking benchmarks.

## Development setup

Requires Python 3.10 or newer. CI targets Python 3.10 and 3.13. From the
repository root, create and activate a virtual environment:

```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

```sh
# Linux / macOS
python3 -m venv .venv
. .venv/bin/activate
```

Then install and check the package:

```sh
python -m pip install -e ".[dev]"
tracevision --version
python -m tracevision --help
python -m compileall -q src tests
python -m unittest discover -s tests -v
python -m build
python -m pip check
```

These checks require no GPU, model weights, or datasets. Installation downloads
build tooling; the package has no runtime dependencies. Artificial byte
fixtures test integrity contracts only, not empirical video performance.

## Data integrity tools

After obtaining and reviewing an official real dataset, explicitly declare
local frame sequences in a selection JSON. The
[preparation instructions](docs/data-preparation.md) define its schema,
official acquisition routes, commands and remaining acceptance gates.

```sh
python -m tracevision data manifest --help
python -m tracevision data verify --help
```

Manifests record source/release/terms metadata, exact selected splits and
relative file paths, byte sizes and SHA-256 hashes. Verification detects
missing/changed files, declared group leakage, copied frame bytes across splits
and invalid declared continuity. It does not decode media, parse object ground
truth, establish licensing permission, or prove every form of leakage absent.
No third-party data is distributed with the project.

## Engineering direction

The planned processing path is video → detection → tracking → evaluation and
failure analysis → events → evidence-grounded explanations. Model libraries
will sit behind project-owned interfaces. This architecture is not yet
implemented; see [engineering decisions](docs/engineering.md).

The next milestone is to unblock official acquisition, validate actual media
and identity annotations, implement one dataset adapter and freeze a small
real development subset. Detection and GPU execution follow that milestone;
see the [Phase 2 prerequisites](docs/data-preparation.md#reproduction-workspace-and-phase-2-gate).

Later milestones cover tracking evaluation, failure inspection, tested event
rules, grounded multimodal evaluation, backend interfaces, benchmarks, and a
free static demo backed by real precomputed results.

All published quality and performance claims must follow the
[dataset and benchmark policy](docs/data-and-benchmarks.md).

## License

TraceVision source is licensed under [MIT](LICENSE). External code, datasets,
and model weights retain their own terms and require review before adoption.
