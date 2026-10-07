"""CPU-only inventories of explicitly selected local frame sequences.

These checks establish byte integrity, not provenance, annotation correctness,
image decodability, legal permission, or suitability for a benchmark.
"""

import hashlib
import json
import math
from datetime import datetime
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit


class DataError(ValueError):
    """Invalid selection or changed local data."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DataError(message)


def _keys(value: object, expected: set[str], label: str) -> None:
    _require(isinstance(value, dict), f"{label} must be an object")
    _require(set(value) == expected, f"{label} fields must be {sorted(expected)}")


def _text(value: object, label: str) -> None:
    _require(isinstance(value, str) and bool(value.strip()), f"{label} must be nonempty text")


def _integer(value: object, label: str) -> None:
    _require(type(value) is int and value >= 0, f"{label} must be a nonnegative integer")


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        _require(key not in result, f"duplicate JSON field: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise DataError(f"invalid JSON: {path}") from error


def canonical_json(value: dict) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def _relative(value: object) -> PurePosixPath:
    _text(value, "file path")
    _require("\\" not in value and ":" not in value, "paths must be portable POSIX relative paths")
    path = PurePosixPath(value)
    _require(not path.is_absolute() and str(path) == value, f"noncanonical path: {value}")
    _require(all(part not in (".", "..") for part in path.parts), f"unsafe path: {value}")
    _require(bool(path.parts), "empty path")
    for part in path.parts:
        _require(not part.endswith((".", " ")), f"nonportable path: {value}")
        _require(not any(c in part for c in '<>"|?*') and not any(ord(c) < 32 for c in part),
                 f"nonportable path: {value}")
        base = part.split(".")[0].upper()
        reserved = {"CON", "PRN", "AUX", "NUL"} | {f"{p}{i}" for p in ("COM", "LPT") for i in range(1, 10)}
        _require(base not in reserved, f"nonportable path: {value}")
    return path


def file_record(root: Path, relative: str) -> dict:
    path = root
    for part in _relative(relative).parts:
        path /= part
        _require(not path.is_symlink(), f"symlink not allowed: {relative}")
    _require(path.is_file(), f"missing regular file: {relative}")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(block)
            digest.update(block)
    _require(size > 0, f"empty file: {relative}")
    return {"path": relative, "size_bytes": size, "sha256": digest.hexdigest()}


def validate_selection(selection: dict) -> None:
    _keys(selection, {"schema_version", "data_kind", "source", "selection_reason", "sequences"}, "selection")
    _require(type(selection["schema_version"]) is int and selection["schema_version"] == 1,
             "unsupported selection schema")
    _require(selection["data_kind"] in ("real", "unit-test"), "invalid data_kind")
    _text(selection["selection_reason"], "selection_reason")
    source = selection["source"]
    _keys(source, {"dataset", "version", "official_url", "terms_url", "license", "retrieved_at", "provenance_notes"}, "source")
    for key, value in source.items():
        _text(value, f"source.{key}")
    for key in ("official_url", "terms_url"):
        url = urlsplit(source[key])
        _require(url.scheme == "https" and bool(url.hostname) and not url.username and not url.password,
                 f"source.{key} must be an HTTPS URL without credentials")
    try:
        timestamp = datetime.fromisoformat(source["retrieved_at"].replace("Z", "+00:00"))
    except ValueError as error:
        raise DataError("retrieved_at must be an ISO timestamp with timezone") from error
    _require(timestamp.utcoffset() is not None, "retrieved_at must include a timezone")
    sequences = selection["sequences"]
    _require(isinstance(sequences, list) and bool(sequences), "sequences must be a nonempty list")
    ids, groups, paths, splits = set(), {}, {}, set()
    for sequence in sequences:
        _keys(sequence, {"id", "group", "split", "fps", "frames", "annotations"}, "sequence")
        for key in ("id", "group", "split"):
            _text(sequence[key], key)
        _require(sequence["id"].casefold() not in ids, "duplicate sequence id")
        ids.add(sequence["id"].casefold())
        split = sequence["split"]
        _require(split in ("train", "validation", "test"), "invalid split")
        splits.add(split)
        group = sequence["group"].casefold()
        _require(group not in groups or groups[group] == split, "scene/source group crosses splits")
        groups[group] = split
        fps = sequence["fps"]
        _require(type(fps) in (int, float) and math.isfinite(fps) and fps > 0, "fps must be finite and positive")
        frames = sequence["frames"]
        _require(isinstance(frames, list) and bool(frames), "frames must be a nonempty list")
        previous = None
        for frame in frames:
            _keys(frame, {"index", "path"}, "frame")
            _integer(frame["index"], "frame index")
            _require(previous is None or frame["index"] == previous + 1,
                     "frame indices must be ordered and contiguous")
            previous = frame["index"]
        annotations = sequence["annotations"]
        _require(isinstance(annotations, list) and bool(annotations), "annotations must be a nonempty list")
        for name in annotations:
            _text(name, "annotation path")
        _require(len(set(annotations)) == len(annotations), "duplicate annotation path")
        for role, names in (("frame", [f["path"] for f in frames]), ("annotation", annotations)):
            for name in names:
                _relative(name)
                folded = name.casefold()
                if folded in paths:
                    old_name, old_role = paths[folded]
                    # A shared full-dataset annotation JSON is legitimate.
                    _require(name == old_name and role == old_role == "annotation",
                             "reused frame, role conflict, or case-colliding path")
                paths[folded] = (name, role)
    _require(splits == {"train", "validation", "test"}, "declare nonempty train, validation, and test splits")


def build_manifest(root: Path, selection: dict) -> dict:
    validate_selection(selection)
    _require(root.is_dir(), f"data root is not a directory: {root}")
    root = root.resolve()
    records = {}
    frame_splits = {}
    for sequence in selection["sequences"]:
        names = [f["path"] for f in sequence["frames"]] + sequence["annotations"]
        for name in names:
            if name not in records:
                records[name] = file_record(root, name)
        for frame in sequence["frames"]:
            digest = records[frame["path"]]["sha256"]
            split = sequence["split"]
            _require(digest not in frame_splits or frame_splits[digest] == split,
                     "identical frame bytes cross splits")
            frame_splits[digest] = split
    # Hashes and split metadata are deterministic. Local paths and wall-clock
    # execution time are deliberately excluded; retrieval time is in source.
    return {"schema_version": 1, "scope": "local-file-integrity-only", "selection": selection,
            "files": [records[name] for name in sorted(records)]}


def verify_manifest(root: Path, manifest: dict) -> dict:
    _keys(manifest, {"schema_version", "scope", "selection", "files"}, "manifest")
    _require(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1,
             "unsupported manifest schema")
    _require(manifest["scope"] == "local-file-integrity-only", "invalid manifest scope")
    _require(isinstance(manifest["files"], list), "manifest files must be a list")
    for record in manifest["files"]:
        _keys(record, {"path", "size_bytes", "sha256"}, "file record")
        _relative(record["path"])
        _integer(record["size_bytes"], "size_bytes")
        digest = record["sha256"]
        _require(isinstance(digest, str) and len(digest) == 64 and all(c in "0123456789abcdef" for c in digest),
                 "invalid SHA-256")
    expected = build_manifest(root, manifest["selection"])
    _require(canonical_json(manifest) == canonical_json(expected), "manifest mismatch: bytes or inventory changed")
    return {"status": "verified", "scope": manifest["scope"],
            "data_kind": manifest["selection"]["data_kind"], "files": len(expected["files"]),
            "size_bytes": sum(f["size_bytes"] for f in expected["files"]),
            "frames": sum(len(s["frames"]) for s in manifest["selection"]["sequences"])}
