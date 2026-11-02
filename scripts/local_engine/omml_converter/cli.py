"""Command-line interface for omml-converter."""

from __future__ import annotations

import argparse
import logging
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .converter import convert

def _require_converter_license():
    """Kiểm tra bản quyền trước khi chạy CLI chuyển đổi."""
    import sys, os
    try:
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        scripts_dir = os.path.dirname(os.path.dirname(cur_dir))
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        import license_manager
        ok, payload, err = license_manager.check_current_license()
        if not ok:
            raise PermissionError(f"MathType Converter chưa kích hoạt bản quyền hợp lệ: {err}")
    except ImportError:
        raise PermissionError("LỖI BẢN QUYỀN: Không tìm thấy license_manager.py.")

_require_converter_license()


def _package_version() -> str:
    try:
        return version("omml-converter")
    except PackageNotFoundError:  # pragma: no cover - source checkout without install
        return "0.0.0+unknown"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="omml-converter",
        description="Convert OMML equations in a .docx to MathType OLE objects.",
    )
    parser.add_argument("input", help="Input .docx file")
    parser.add_argument(
        "-o",
        "--output",
        help="Output .docx file (default: <input>_mathtype.docx)",
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show per-equation conversion details",
    )
    verbosity.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only print errors",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_package_version()}",
    )
    return parser


def _configure_logging(*, verbose: bool, quiet: bool) -> None:
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level, format="%(message)s", stream=sys.stderr, force=True)


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code.

    Exit codes: ``0`` success, ``1`` bad input or one-or-more equation failures,
    ``2`` argument-parsing errors (handled by argparse).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    _configure_logging(verbose=args.verbose, quiet=args.quiet)

    inp = Path(args.input)
    if not inp.exists():
        print(f"Error: file not found: {inp}", file=sys.stderr)
        return 1
    if inp.suffix.lower() != ".docx":
        print(f"Error: expected a .docx file, got: {inp}", file=sys.stderr)
        return 1

    out = Path(args.output) if args.output else inp.with_name(inp.stem + "_mathtype.docx")

    try:
        summary = convert(str(inp), str(out))
    except Exception as exc:  # noqa: BLE001 — surface any failure as exit code 1
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Always print the final summary (even in quiet mode) to stdout.
    print(f"Converted {summary.converted}/{summary.found} equation(s) → {out}")
    if summary.skipped:
        print(f"  {summary.skipped} skipped (empty content)", file=sys.stderr)
    if summary.errors:
        print(f"  {summary.errors} failed — see messages above", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())