"""Command-line entry point for the installed package."""

import argparse
from collections.abc import Sequence

from tracevision import __version__


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tracevision",
        description="TraceVision package tools. Video processing is not implemented yet.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.parse_args(argv)
    parser.print_help()
    return 0
