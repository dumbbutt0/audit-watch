#!/usr/bin/env python3
"""
collect_poc_results.py — Run a PoC test command and record its execution (deterministic, no LLM).

This script RECORDS execution only — it decides nothing about proof validity (that is validate_poc.py's
job). It runs the user-supplied command, captures stdout/stderr, saves the raw log, records the exit code,
and extracts a basic pass/fail signal (forge `[PASS]/[FAIL]`, cargo `test result: ok/FAILED`, or generic
non-zero exit).

Example:
    python scripts/collect_poc_results.py \\
      --finding-id DPF-036 \\
      --test-file test/MarketplaceTransferPlots.t.sol \\
      --test-name test_transferPlots_DoesNotDecrementAllowance_FieldZero \\
      --command "forge test --match-test test_transferPlots_DoesNotDecrementAllowance_FieldZero -vvv"

Writes:
    output/poc_validation/raw/<finding_id>_<test_name>.log
    output/poc_validation/collected_results.json   (one entry per finding_id+test_name, upserted)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

FORGE_PASS = re.compile(r"\[PASS\]")
FORGE_FAIL = re.compile(r"\[FAIL")
CARGO_OK = re.compile(r"test result:\s*ok\b")
CARGO_FAIL = re.compile(r"test result:\s*FAILED\b|FAILED\b")


def extract_pass_fail(stdout: str, stderr: str, exit_code: int) -> str:
    """Best-effort test pass/fail signal. Records observation only — not a proof verdict."""
    blob = (stdout or "") + "\n" + (stderr or "")
    if exit_code != 0:
        # non-zero almost always means failure/compile error; still note if a [PASS] appeared
        if FORGE_FAIL.search(blob) or CARGO_FAIL.search(blob):
            return "failed"
        if "error" in blob.lower() or "compilation" in blob.lower():
            return "error"
        return "failed"
    if FORGE_FAIL.search(blob) or CARGO_FAIL.search(blob):
        return "failed"
    if FORGE_PASS.search(blob) or CARGO_OK.search(blob):
        return "passed"
    return "unknown"


def _safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", s or "test")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--finding-id", required=True)
    ap.add_argument("--test-file", default=None)
    ap.add_argument("--test-name", default=None)
    ap.add_argument("--command", required=True)
    ap.add_argument("--cwd", default=None, help="working directory for the command (default: repo root)")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    raw_dir = audit_path("output", "poc_validation", "raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    log_path = raw_dir / f"{_safe_name(args.finding_id)}_{_safe_name(args.test_name)}.log"

    started = datetime.now(timezone.utc).isoformat()
    try:
        proc = subprocess.run(
            args.command, shell=True, capture_output=True, text=True,
            cwd=args.cwd, timeout=args.timeout,
        )
        exit_code = proc.returncode
        stdout, stderr = proc.stdout, proc.stderr
        timed_out = False
    except subprocess.TimeoutExpired as e:
        exit_code = 124
        stdout = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = ((e.stderr or b"").decode() if isinstance(e.stderr, bytes) else (e.stderr or "")) + "\n[collect_poc_results] TIMEOUT"
        timed_out = True

    log_path.write_text(
        f"# command: {args.command}\n# started: {started}\n# exit_code: {exit_code}\n"
        f"# timed_out: {timed_out}\n\n===== STDOUT =====\n{stdout}\n\n===== STDERR =====\n{stderr}\n"
    )

    test_status = extract_pass_fail(stdout, stderr, exit_code)
    entry = {
        "finding_id": args.finding_id,
        "test_file": args.test_file,
        "test_name": args.test_name,
        "command": args.command,
        "command_exit_code": exit_code,
        "timed_out": timed_out,
        "test_status": test_status,
        "raw_result_path": str(log_path.relative_to(audit_path("."))) if str(log_path).startswith(str(audit_path("."))) else str(log_path),
        "stdout_excerpt": (stdout or "")[-4000:],
        "stderr_excerpt": (stderr or "")[-2000:],
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }

    coll_path = audit_path("output", "poc_validation", "collected_results.json")
    existing = {"results": []}
    if coll_path.exists():
        try:
            existing = json.loads(coll_path.read_text())
        except (json.JSONDecodeError, OSError):
            existing = {"results": []}
    results = [r for r in existing.get("results", [])
               if not (r.get("finding_id") == args.finding_id and r.get("test_name") == args.test_name)]
    results.append(entry)
    coll_path.write_text(json.dumps(
        {"generated_at": datetime.now(timezone.utc).isoformat(), "results": results}, indent=2))

    if not args.quiet:
        print(f"Collected {args.finding_id} / {args.test_name}: exit={exit_code} status={test_status}")
        print(f"  raw log: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
