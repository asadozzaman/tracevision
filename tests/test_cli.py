"""Exercise installed entry points without models, datasets, or accelerators."""

import subprocess
import sys
import unittest
from importlib.metadata import version


class CLITests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "tracevision", *args],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def test_module_version_matches_distribution(self) -> None:
        result = self.run_cli("--version")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), f"tracevision {version('tracevision')}")
        self.assertEqual(result.stderr, "")

    def test_console_entry_point(self) -> None:
        result = subprocess.run(
            ["tracevision", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), f"tracevision {version('tracevision')}")

    def test_help_and_no_arguments(self) -> None:
        for args in [(), ("--help",)]:
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("--version", result.stdout)
                self.assertIn("not implemented yet", result.stdout)

    def test_unimplemented_command_fails(self) -> None:
        result = self.run_cli("benchmark")
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid choice", result.stderr)


if __name__ == "__main__":
    unittest.main()
