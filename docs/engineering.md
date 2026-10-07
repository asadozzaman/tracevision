# Engineering decisions

## Foundation

The package uses a `src` layout so installation checks exercise packaged code
rather than accidental imports from the repository root. Python 3.10 is the
minimum version. Setuptools builds wheels and source distributions; the build
backend and direct development tool are pinned in `pyproject.toml`. Transitive
tool dependencies are not locked, so this is not a claim of bit-for-bit builds.
The distribution metadata is the single source of the package version.

The foundation CLI initially provided only help and version information. Standard-library
`unittest` checks installed module and console entry points, help, and rejection
of unsupported commands. CI builds a source distribution and a wheel from it,
installs the wheel, and runs those checks on Windows and Linux. CI does not
require accelerators or download models or datasets. Phase 1 preparation adds
standard-library selection/file-integrity commands and CPU tests. It does not
yet include a dataset-specific adapter or an accepted real subset. See the
[implemented contract and its limits](data-preparation.md).

MIT applies to original project source. Dependency code, model weights, and
datasets need separate license and compatibility review before integration.
No detector, tracker, dataset, or VLM is committed by this decision.

## Boundaries for subsequent implementation

- Normalize detector and tracker outputs into typed project-owned objects.
  External framework result types stay inside adapters. Add domain types when
  a working pipeline needs them, rather than creating empty abstractions now.
- Introduce one device resolver with the first inference adapter. `auto` selects
  CUDA when available and otherwise CPU. An explicit unavailable device must
  fail clearly. Record both requested and resolved devices in run artifacts.
- Use the same package and explicit configuration on Windows, Kaggle, and
  Linux. Keep GPU dependencies optional. CPU tests remain small; substantive
  GPU experiments use free Kaggle capacity when available.
- Integrate an established tracking implementation. Identity-annotated ground
  truth and an established evaluator are required before tracking accuracy
  claims. Track counts and annotated videos are inspection aids, not metrics.
- Evaluate failure cases before adding event rules. Events use track evidence;
  a later VLM consumes selected evidence and must cite frame/time/track
  references. Separate measured CV facts from generated explanations.
- Prefer offline results and a static public demo. No capability may depend on
  an assumed always-on free GPU.

These boundaries describe intended implementation, not existing capabilities.

## Independent development and changes

Use independently sourced public data, public models, and original code.
Employer/client code, datasets, videos, model weights, infrastructure, and
credentials are outside this project's scope. Do not use office compute or
private cloud resources for experiments.

Keep work in reviewable phase branches. Inspect existing code before extending
it; test each implemented contract and update documentation from actual
execution. Public claims must point to inspectable evidence. Keep raw data,
weights, credentials, large generated media, and temporary tooling output out
of commits. Only introduce directories when they contain useful implementation.
