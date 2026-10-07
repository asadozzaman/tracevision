"""Command-line entry point for the installed package."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from tracevision import __version__
from tracevision.data import build_manifest, canonical_json, read_json, verify_manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tracevision",
        description="TraceVision data integrity tools. Video inference is not implemented yet.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command")
    data = commands.add_parser("data", help="Inventory or verify explicitly selected local data")
    actions = data.add_subparsers(dest="action", required=True)
    create = actions.add_parser("manifest", help="Hash a declared selection; never overwrite a manifest")
    create.add_argument("--root", type=Path, required=True)
    create.add_argument("--selection", type=Path, required=True)
    create.add_argument("--output", type=Path, required=True)
    verify = actions.add_parser("verify", help="Rehash local files against a trusted manifest")
    verify.add_argument("--root", type=Path, required=True)
    verify.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "data":
        try:
            if args.action == "manifest":
                manifest = build_manifest(args.root, read_json(args.selection))
                encoded = canonical_json(manifest)
                args.output.parent.mkdir(parents=True, exist_ok=True)
                with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                    stream.write(encoded)
                print(canonical_json({"status": "created", "scope": manifest["scope"],
                                      "data_kind": manifest["selection"]["data_kind"],
                                      "files": len(manifest["files"])}), end="")
            else:
                print(canonical_json(verify_manifest(args.root, read_json(args.manifest))), end="")
        except (OSError, ValueError) as error:
            parser.exit(2, f"tracevision: {error}\n")
        return 0
    parser.print_help()
    return 0
