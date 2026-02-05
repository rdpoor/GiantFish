"""Minimal CLI entry points."""
from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="GiantFish CLI")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    args = parser.parse_args()

    if args.version:
        print("giantfish 0.1.0")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
