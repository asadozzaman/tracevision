# Local data integrity preparation

**Implemented:** explicit frame-selection validation, SHA-256/byte-size
inventory creation, and verification against a previously trusted manifest.
**Pending:** accepted dataset, actual acquisition/preparation adapter, decoded
media validation, ground-truth validation and a frozen real subset.
These commands are useful Phase 1 preparation; they do not complete Phase 1.

## Obtain data through its official route

1. Review [the candidate comparison](data-selection.md). Confirm the actual
   downloaded release terms permit the intended research use. Keep dataset
   terms separate from TraceVision's MIT source license.
2. For ROAD, follow the author's linked Drive folders for train/validation and
   test. The author script `road/get_dataset.sh` identifies the train/validation
   video and annotation files. Inspect it before execution: it contains old
   cookie handling and a TLS-verification bypass that TraceVision does not
   adopt. Use a supported downloader or the official browser download instead.
   For ROAD-Waymo, register/sign in to Waymo and use the community contribution
   linked by its authors. For TUMTraf-A, register through its project portal and
   confirm the accident release. For KITTI, use the official tracking page's
   account/download route for left color images and training labels. Do not
   treat the hidden official test ground truth as locally available.
3. SVMOT's author release supports an explicit archive integrity check:
   obtain `svmot_data_v1.0.zip`, `SHA256SUMS`, `train.txt`, `test.txt`,
   `by_scene.json`, and `README_RELEASE_v1.0.md` from
   <https://zenodo.org/records/19468203>. Keep them in `data/svmot-release/`.
   Compare all file hashes with the author's checksums before extraction. The
   archive is about 18.34 GB in decimal units, excluding extracted files.
   Archive retrieval and extraction have **not** succeeded in this session.

For that release, the following CPU command checks downloaded release files:

```sh
python -c "from pathlib import Path; import hashlib; p=Path('data/svmot-release'); expected={line.split()[1]:line.split()[0] for line in (p/'SHA256SUMS').read_text().splitlines()}; actual={name:hashlib.file_digest((p/name).open('rb'),'sha256').hexdigest() for name in expected}; assert actual==expected, 'release checksum mismatch'"
```

`hashlib.file_digest` requires Python 3.11+. On Python 3.10, use a streaming
SHA-256 implementation or an OS SHA-256 utility. This command requires every
listed release file; having only the split metadata is insufficient.

No third-party videos, annotations, models or archives are committed or
uploaded to Kaggle. A private upload also requires redistribution permission.
Downloads and extraction must remain under ignored `data/` or outside Git.

## Accept a small real subset

After successful acquisition, inspect original annotations and decode the
selected media on CPU. Declare exact original sequence IDs, physical
scene/source-drive groups, source split, original frame indices, timebase,
classes, identities, ignored regions and annotation coverage. Preserve original
files and IDs. Keep continuous frame windows; never randomly split frames.
Hold out separate source groups before any model tuning.

Start with a modest fixed continuous window per selected sequence, not a full
training corpus. The exact IDs and window sizes depend on the inspected real
inventory and are **not chosen yet**. If a dataset lacks a validation split,
document a scene-separated holdout from its training groups. It is a project
development split, not the dataset's official benchmark split. Shared full
annotation JSON files can legitimately describe several splits; every relevant
frame/identity link still needs dataset-specific validation.

Decode success, bounding-box validity, annotated-vs-unannotated frames, identity
consistency and class mapping need a tested dataset adapter. The integrity
tool below does not implement these checks. Record missing annotation coverage
instead of interpreting an absent label as an empty scene. Scene similarity
and pretrained-model contamination remain separate review questions.

## Selection schema v1

Write an explicit UTF-8 JSON selection after the real inventory is inspected.
All fields are required, unknown fields are rejected, and duplicate JSON keys
are rejected. Metadata strings cannot be empty. HTTPS source/terms URLs must
not contain credentials. `retrieved_at` is an ISO timestamp with a timezone.

| Location | Fields and meaning |
| --- | --- |
| Top level | `schema_version`: integer `1`; `data_kind`: `real` or `unit-test`; `source`: object; `selection_reason`: rationale; `sequences`: nonempty list |
| source | `dataset`, `version`, `official_url`, `terms_url`, `license`, `retrieved_at`, `provenance_notes`: explicit source/release/terms identifiers and reviewed acquisition details |
| Each sequence | `id`: original sequence ID; `group`: physical scene/source drive; `split`: `train`, `validation` or `test`; `fps`: finite positive source FPS; `frames`: ordered list; `annotations`: nonempty list of relative annotation paths |
| Each frame | `index`: original nonnegative integer frame number; `path`: relative POSIX file path under the data root |

Every split must contain at least one sequence. Indices within each sequence
must be consecutive. Sequence IDs are unique and a group cannot cross splits;
IDs/groups are checked without case sensitivity. Paths reject traversal,
absolute paths, Windows reserved names and case collisions. Symlink files and
symlink parents are rejected. Frame paths cannot be reused; shared annotation
files are allowed. All selected files must exist and be nonempty. Hashing is
streamed in 1 MiB blocks. Identical frame bytes across splits are rejected;
identical consecutive frames within a split may be legitimate and are allowed.

`data_kind=unit-test` is reserved for artificial software fixtures. It never
establishes empirical performance. The `real` value is a caller declaration,
not an automated authenticity determination. A nonempty license field also
does not establish legal permission. Review those facts independently.

## Create and verify an inventory

From the installed repository environment, once `data/selection.json` and the
selected local files actually exist:

```sh
python -m tracevision data manifest --root data/development --selection data/selection.json --output datasets/manifests/development-v1.json
python -m tracevision data verify --root data/development --manifest datasets/manifests/development-v1.json
```

The first command refuses to overwrite an existing output. Both commands use
CPU and the Python standard library only; neither accesses the network. They
return JSON summaries on success and exit `2` for invalid data or I/O errors.
The manifest contains the full selection and sorted unique file records with
exact relative path, byte count, and SHA-256. Serialization is deterministic
for the same selection and bytes, including the supplied retrieval timestamp.
No machine-specific absolute path is recorded.

Commit a reviewed **real** manifest only after all acceptance gates pass.
Independently pin its SHA-256 and source revision in future experiment records;
verification assumes the manifest itself is trusted. Rehash every selected
file before a run. A changed inventory requires a new manifest version. Files
outside the explicitly selected inventory are not checked. Do not rewrite a
trusted manifest merely to make changed data pass.

The successful summary deliberately says `local-file-integrity-only`. It does
not prove media decode success, true temporal adjacency, annotation quality,
identity correctness, source authenticity, license compliance, perceptual
deduplication, or absence of every kind of data leakage. Group labels and frame
indices are declared metadata; the tool cannot discover true scene identities.

## Reproduction workspace and Phase 2 gate

For continued acquisition, use a personal Codex workspace with this repository,
Python 3.10+ (CI uses 3.10 and 3.13), Git read/write permission, sufficient
personal disk space and outbound HTTPS to the chosen official source. For
video sources, provide CPU FFmpeg/ffprobe and record their versions when an
extraction adapter is implemented. The workspace must not use employer assets
or credentials. No CUDA GPU is required for Phase 1.

Fetch the current remote, check out `feat/phase1-data-integrity`, read both data
policies and this review, and install with `python -m pip install -e ".[dev]"`.
Run `python -m unittest discover -s tests -v` before continuing. Do not resume
the old local dataset branch without inspecting its actual contents.

Phase 2 requires a licensed, obtained, decoded and annotation-validated real
subset; a frozen split/manifest; explicit class/ignore/matching rules; a
reviewed detector/weights license; and an inference/run-evidence contract.
Only then implement detection and record a real baseline. Device selection and
optional Kaggle execution belong to that milestone. GitHub Actions must remain
CPU-only and independent of Kaggle. Tracking, events and VLMs follow later.
