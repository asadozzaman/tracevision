# Dataset and benchmark policy

No datasets or model weights have been selected or downloaded. No experiments
have run. This document defines acceptance criteria for future work, not
benchmark results or an implemented artifact schema.

## Dataset selection and provenance

Use real public video and annotations for quality, event, multimodal, and
performance claims. Synthetic data is restricted to small isolated unit-test
fixtures and must never be presented as empirical validation.

Before accepting a dataset, record:

- Official source, dataset version, retrieval date, and authoritative terms.
  Review access, allowed uses, attribution, and redistribution separately.
- Suitability for the intended task: scene types, camera motion, classes,
  annotation granularity, frame coverage, identity labels, and known gaps.
- Exact split and sequence/frame selection, including the selection method.
  Preserve sequence continuity for tracking; do not mix tuning and evaluation.
- Download and extracted storage requirements, access prerequisites, and
  whether a fixed small subset is practical on free compute.
- Reproducible preparation commands and a manifest with relative paths,
  file sizes, SHA-256 checksums, and annotation/source version identifiers.

Compare BDD100K with suitable established road-scene alternatives using these
criteria. Assess a separate identity-annotated MOT benchmark only where it
answers a defined tracking question. Pedestrian or non-road results must not be
generalized to road traffic without supporting evaluation.

An unofficial mirror needs verification against the official source. Do not
upload third-party data to Kaggle or demo hosting without explicit permission
in its terms. Prefer preparation scripts and manifests to redistributed data.
Freeze accepted manifests; changes require a new version and documented reason.
Keep downloaded data outside Git. Store future manifests under
`datasets/manifests/`.

## Experiment evidence

Each recorded benchmark must identify:

- Run ID, UTC date/time, code commit SHA, and whether the working tree is dirty.
  Published baselines use a clean commit; exploratory runs are labeled.
- OS, Python and relevant package versions, CPU/GPU hardware, resolved device,
  and resource limits where available.
- Model source, identifier/version, weights checksum, and license; dataset
  version, split, manifest checksum, and exact evaluated sequence/frame counts.
- Effective configuration, including preprocessing, confidence/NMS thresholds,
  image size, tracker settings, and seeds where meaningful.
- Timing boundaries, warm-up policy, batch size, repetitions, synchronization
  for asynchronous GPU execution, and inclusion/exclusion of decode and I/O.

Keep source-video FPS, inference throughput, and end-to-end throughput distinct.
Report measured values only. Retain skipped frames, failed sequences, and
partial-run status; do not silently improve scores by omitting failures.

Quality evaluation requires applicable ground truth and a declared protocol.
For tracking, justify selected metrics such as HOTA, IDF1, MOTA, identity
switches, and FP/FN. Record evaluator version, matching thresholds, class
mapping, ignored regions, and aggregation rules. Do not substitute the number
of emitted track IDs for accuracy. Failure records should reference source
sequence, frame/time, object/track identity, and evidence where available;
distinguish observed errors from hypothesized causes.

## Run artifacts and publication

Future runs should write to `artifacts/<run-id>/`, with `config.json`,
`environment.json`, and `summary.json`. Add task-specific outputs only when
implemented: frame/track records, metrics, failure records, event records, and
evidence references. Define and validate schemas alongside their producers.
No placeholder scores or fabricated example runs belong in the repository.

Generated runs are ignored by Git. Publish a deliberately reviewed compact
report and machine-readable evidence under `benchmarks/<run-id>/` only after
execution and inspection. Retain the exact reproduction command and link to
the full outputs where their licenses permit. Selected demo media requires a
separate redistribution review.

Kaggle experiments must use the same source revision and interfaces as local
runs, with recorded dependencies, configuration, model, and data versions.
If GPU execution is unavailable, publish only reproducible preparation and
mark the experiment pending. Normal CI must remain independent of Kaggle.
