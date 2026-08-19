"""Command-line interface.

    preaudit scan <path> [--format text|markdown|json] [--strict] [--exit-zero] [--output FILE]
    preaudit sandbox <path> [-o DIR] [--force]

Exit codes:
    0  success (scan: overall risk below threshold / --exit-zero; sandbox: artifacts written)
    2  scan: overall risk at/above the threshold (default HIGH; --strict lowers to MEDIUM)
    1  usage / IO error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .findings import Severity
from .report import render
from .scanner import run_scan
from .sandbox import generate_sandbox, DEFAULT_OUT_DIR


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="preaudit",
        description="Static, offline preflight scanner that quarantines an unknown codebase "
                    "(prompt-injection traps, malicious lifecycle/build scripts, exposed secrets) "
                    "BEFORE you install deps, run tests, or feed it to an AI agent.",
    )
    p.add_argument("--version", action="version", version=f"preaudit-guard {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan a file or directory and report risk signals.")
    scan.add_argument("path", help="File or directory to scan.")
    scan.add_argument("--format", choices=["text", "markdown", "json"], default="text",
                      help="Output format (default: text).")
    scan.add_argument("--strict", action="store_true",
                      help="Block at MEDIUM risk instead of the default HIGH (exit code 2).")
    scan.add_argument("--exit-zero", action="store_true",
                      help="Always exit 0 even when risk meets the threshold (report only).")
    scan.add_argument("--output", "-o", metavar="FILE",
                      help="Write the report to FILE instead of stdout.")

    sb = sub.add_parser(
        "sandbox",
        help="Generate quarantine artifacts (network-denied container, run wrapper, "
             "preflight report, and a metadata-only agent_context_safe.md).",
    )
    sb.add_argument("path", help="Repository directory to quarantine.")
    sb.add_argument("--output-dir", "-o", metavar="DIR", default=DEFAULT_OUT_DIR,
                    help=f"Directory to write artifacts into (default: ./{DEFAULT_OUT_DIR}).")
    sb.add_argument("--force", action="store_true",
                    help="Write into the output directory even if it is non-empty.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.command == "scan":
        return _cmd_scan(args)
    if args.command == "sandbox":
        return _cmd_sandbox(args)
    return 1


def _cmd_scan(args) -> int:
    target = Path(args.path)
    if not target.exists():
        print(f"error: path does not exist: {target}", file=sys.stderr)
        return 1

    result = run_scan(target)
    rendered = render(result, args.format)

    if args.output:
        try:
            Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        except OSError as e:
            print(f"error: cannot write {args.output}: {e}", file=sys.stderr)
            return 1
    else:
        print(rendered)

    threshold = Severity.MEDIUM if args.strict else Severity.HIGH
    if result.overall >= threshold and not args.exit_zero:
        return 2
    return 0


def _cmd_sandbox(args) -> int:
    target = Path(args.path)
    if not target.exists() or not target.is_dir():
        print(f"error: not a directory: {target}", file=sys.stderr)
        return 1

    out = Path(args.output_dir)
    if out.exists() and any(out.iterdir()) and not args.force:
        print(f"error: output dir {out} is not empty (use --force to write anyway).", file=sys.stderr)
        return 1

    try:
        result, written = generate_sandbox(target, out)
    except OSError as e:
        print(f"error: cannot generate sandbox: {e}", file=sys.stderr)
        return 1

    print(f"PreAudit Guard — sandbox generated for {target}")
    print(f"  Overall risk: {result.overall.label}  ({len(result.findings)} signals)")
    print(f"  Artifacts in {out}/:")
    for p in written:
        print(f"   - {p.name}")
    print()
    print(f"  Next: review {out / 'SECURITY_PREFLIGHT.md'}, then run:  bash {out / 'run-quarantine.sh'}")
    print("  Hand an AI agent ONLY agent_context_safe.md — never the raw repo — until reviewed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
