# TraceVision

TraceVision is an early-stage project for road-scene video intelligence, with
an emphasis on reproducible evaluation and inspectable tracking failures.

## Current state

**Implemented:** an installable Python package, version/help commands, package
smoke tests, and CPU-only CI configuration for Windows and Linux.

**Not implemented:** dataset preparation, inference, tracking, evaluation,
events, multimodal explanations, an API, or a public demo. No model or dataset
has been selected. No accuracy or performance results are available.

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
build tooling; the package has no runtime dependencies. The CLI currently only
reports version and help information.

## Engineering direction

The planned processing path is video → detection → tracking → evaluation and
failure analysis → events → evidence-grounded explanations. Model libraries
will sit behind project-owned interfaces. This architecture is not yet
implemented; see [engineering decisions](docs/engineering.md).

The next milestone is dataset selection and a verifiable preparation pipeline.
It will compare established public road-scene sources for licensing,
annotations, storage, and free-compute feasibility before selecting a fixed
development subset. Detection and GPU execution follow that milestone.

Later milestones cover tracking evaluation, failure inspection, tested event
rules, grounded multimodal evaluation, backend interfaces, benchmarks, and a
free static demo backed by real precomputed results.

All published quality and performance claims must follow the
[dataset and benchmark policy](docs/data-and-benchmarks.md).

## License

TraceVision source is licensed under [MIT](LICENSE). External code, datasets,
and model weights retain their own terms and require review before adoption.
