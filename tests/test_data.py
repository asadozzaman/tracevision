"""Artificial byte fixtures test software contracts, never dataset quality."""

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tracevision.data import DataError, build_manifest, canonical_json, read_json, verify_manifest


class DataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.selection = {
            "schema_version": 1, "data_kind": "unit-test", "selection_reason": "Software unit test only",
            "source": {"dataset": "artificial-byte-fixture", "version": "1",
                       "official_url": "https://example.org/fixture", "terms_url": "https://example.org/terms",
                       "license": "test-fixture", "retrieved_at": "2026-10-07T00:00:00Z",
                       "provenance_notes": "Generated here, not real video or benchmark evidence."},
            "sequences": [],
        }
        for split in ("train", "validation", "test"):
            frames = []
            for index in range(3):
                name = f"{split}/{index}.frame"
                path = self.root / name
                path.parent.mkdir(exist_ok=True)
                path.write_bytes(f"artificial {split} {index}".encode())
                frames.append({"index": index, "path": name})
            annotation = f"{split}/labels.txt"
            (self.root / annotation).write_text("fixture only\n", encoding="utf-8")
            self.selection["sequences"].append({"id": split, "group": split, "split": split,
                                                "fps": 10, "frames": frames, "annotations": [annotation]})

    def test_round_trip_and_exact_digest(self):
        manifest = build_manifest(self.root, self.selection)
        self.assertEqual(manifest, build_manifest(self.root, self.selection))
        record = next(r for r in manifest["files"] if r["path"] == "train/0.frame")
        content = (self.root / record["path"]).read_bytes()
        self.assertEqual(record["sha256"], hashlib.sha256(content).hexdigest())
        self.assertEqual(record["size_bytes"], len(content))
        summary = verify_manifest(self.root, json.loads(canonical_json(manifest)))
        self.assertEqual(summary["files"], 12)
        self.assertEqual(summary["frames"], 9)
        self.assertEqual(summary["data_kind"], "unit-test")

    def test_modified_same_size_file_is_detected(self):
        manifest = build_manifest(self.root, self.selection)
        path = self.root / "train/0.frame"
        content = path.read_bytes()
        path.write_bytes(b"X" * len(content))
        with self.assertRaisesRegex(DataError, "mismatch"):
            verify_manifest(self.root, manifest)

    def test_missing_and_empty_files(self):
        for action in ("missing", "empty"):
            with self.subTest(action=action):
                path = self.root / "train/0.frame"
                if action == "missing":
                    path.unlink()
                else:
                    path.write_bytes(b"")
                with self.assertRaises(DataError):
                    build_manifest(self.root, self.selection)

    def test_group_leakage(self):
        self.selection["sequences"][1]["group"] = "TRAIN"
        with self.assertRaisesRegex(DataError, "group crosses splits"):
            build_manifest(self.root, self.selection)

    def test_copied_frame_leakage_across_splits(self):
        (self.root / "test/0.frame").write_bytes((self.root / "train/0.frame").read_bytes())
        with self.assertRaisesRegex(DataError, "identical frame bytes"):
            build_manifest(self.root, self.selection)

    def test_identical_consecutive_frames_within_split_are_allowed(self):
        (self.root / "train/1.frame").write_bytes((self.root / "train/0.frame").read_bytes())
        build_manifest(self.root, self.selection)

    def test_indices_must_be_contiguous_ordered_and_integral(self):
        for indices in ([0, 2, 3], [2, 1, 0], [0, 0, 1], [True, 1, 2], [0, 1.0, 2]):
            with self.subTest(indices=indices):
                selection = copy.deepcopy(self.selection)
                for frame, index in zip(selection["sequences"][0]["frames"], indices):
                    frame["index"] = index
                with self.assertRaises(DataError):
                    build_manifest(self.root, selection)

    def test_unsafe_and_nonportable_paths(self):
        for name in ("../outside", "/tmp/outside", "C:/outside", "train\\0.frame",
                     "train/../0.frame", "train//0.frame", "./train/0.frame", "NUL.txt", "train/file."):
            with self.subTest(name=name):
                selection = copy.deepcopy(self.selection)
                selection["sequences"][0]["frames"][0]["path"] = name
                with self.assertRaises(DataError):
                    build_manifest(self.root, selection)

    def test_reused_and_case_colliding_frame_paths(self):
        for name in ("train/0.frame", "TRAIN/0.frame"):
            selection = copy.deepcopy(self.selection)
            selection["sequences"][0]["frames"][1]["path"] = name
            with self.assertRaisesRegex(DataError, "case-colliding path"):
                build_manifest(self.root, selection)

    def test_shared_dataset_annotation_is_allowed(self):
        for sequence in self.selection["sequences"]:
            sequence["annotations"] = ["train/labels.txt"]
        self.assertEqual(len(build_manifest(self.root, self.selection)["files"]), 10)

    def test_symlink_files_and_parents_are_rejected(self):
        for parent in (False, True):
            with self.subTest(parent=parent):
                link = self.root / ("linked_dir" if parent else "linked_file")
                try:
                    os.symlink(self.root / ("train" if parent else "train/0.frame"), link, target_is_directory=parent)
                except (OSError, NotImplementedError):
                    self.skipTest("symlinks unavailable on this OS/account")
                selection = copy.deepcopy(self.selection)
                selection["sequences"][0]["frames"][0]["path"] = "linked_dir/0.frame" if parent else "linked_file"
                with self.assertRaisesRegex(DataError, "symlink"):
                    build_manifest(self.root, selection)

    def test_bad_metadata_is_rejected(self):
        changes = [("fps", 0), ("fps", float("nan")), ("fps", True), ("annotations", []),
                   ("annotations", [{}]), ("split", "unrecognized"), ("frames", [])]
        for key, value in changes:
            selection = copy.deepcopy(self.selection)
            selection["sequences"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(DataError):
                build_manifest(self.root, selection)
        for key, value in (("license", ""), ("retrieved_at", "2026-10-07"),
                           ("official_url", "https://user:secret@example.org/data")):
            selection = copy.deepcopy(self.selection)
            selection["source"][key] = value
            with self.subTest(key=key), self.assertRaises(DataError):
                build_manifest(self.root, selection)

    def test_omitted_split_is_rejected(self):
        self.selection["sequences"].pop()
        with self.assertRaisesRegex(DataError, "nonempty train"):
            build_manifest(self.root, self.selection)

    def test_inventory_tampering_is_rejected(self):
        for action in ("remove", "extra", "size", "schema"):
            manifest = build_manifest(self.root, self.selection)
            if action == "remove":
                manifest["files"].pop()
            elif action == "extra":
                manifest["files"].append(manifest["files"][0])
            elif action == "size":
                manifest["files"][0]["size_bytes"] = True
            else:
                manifest["schema_version"] = True
            with self.subTest(action=action), self.assertRaises(DataError):
                verify_manifest(self.root, manifest)

    def test_duplicate_json_fields_are_rejected(self):
        path = self.root / "bad.json"
        path.write_text('{"schema_version": 1, "schema_version": 2}', encoding="utf-8")
        with self.assertRaisesRegex(DataError, "duplicate JSON field"):
            read_json(path)

    def test_cli_create_verify_and_no_overwrite(self):
        selection = self.root / "selection.json"
        selection.write_text(canonical_json(self.selection), encoding="utf-8")
        output = self.root / "manifest.json"
        base = [sys.executable, "-m", "tracevision", "data"]
        create = base + ["manifest", "--root", str(self.root), "--selection", str(selection), "--output", str(output)]
        result = subprocess.run(create, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["data_kind"], "unit-test")
        original = output.read_bytes()
        result = subprocess.run(create, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(output.read_bytes(), original)
        verify = base + ["verify", "--root", str(self.root), "--manifest", str(output)]
        result = subprocess.run(verify, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        (self.root / "test/0.frame").write_bytes(b"changed")
        result = subprocess.run(verify, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
