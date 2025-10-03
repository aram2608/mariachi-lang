from __future__ import annotations
from pathlib import Path
import argparse
import sys

from .core.scanner import Scanner


def slurp_file(path: Path) -> str:
    path = Path(path)
    with open(path, "r") as file:
        contents = file.read()
    return contents


def run_file(path: Path) -> int:
    scanner = Scanner(slurp_file(path))
    toks = scanner.scan_tokens()
    for t in toks:
        print(t)
    return 0


def run_repl() -> int:
    print("REPL not implemented.")
    return 0


def main(argv=None) -> int | None:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Mariachi lang cli entry")
    parser.add_argument(
        "--file", "-f", type=Path, default=None, help="Path to Mariachi file."
    )
    args = parser.parse_args(argv)

    if args.file:
        return run_file(args.file)
    else:
        return run_repl()


if __name__ == "__main__":
    raise SystemExit(main())
