#!/usr/bin/env python3
"""
run_poc_tests.py — Run an existing PoC test and record the result.

Usage:
    python scripts/run_poc_tests.py --finding-id AR-001 --repo contracts/2026-04-k2
    python scripts/run_poc_tests.py --all                              # run all generated pocs

Fork PoC support:
    Plans or results that set "fork": true and "fork_chain": "<chain>" will have
    their run_command's ${<CHAIN>_RPC_URL} placeholder substituted from
    config/rpc_endpoints.json (first available RPC for that chain).
    The env var takes precedence: e.g. FLARE_RPC_URL=... overrides the config list.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

POC_DIR  = audit_path("data/poc_queue")
POCS_DIR = audit_path("pocs")

ROOT = Path(__file__).resolve().parent.parent
RPC_CONFIG_PATH = ROOT / "config" / "rpc_endpoints.json"


def resolve_fork_rpc(chain: str) -> str | None:
    """Return the RPC URL for chain. Env var takes priority over config file."""
    config = {}
    if RPC_CONFIG_PATH.exists():
        config = json.loads(RPC_CONFIG_PATH.read_text())
    entry = config.get(chain.lower(), {})
    env_var = entry.get("env_var", f"{chain.upper()}_RPC_URL")
    # Env var takes priority
    if os.environ.get(env_var):
        return os.environ[env_var]
    rpcs = entry.get("rpcs", [])
    return rpcs[0] if rpcs else None


def resolve_run_command(run_command: str, plan: dict, result: dict) -> str:
    """Substitute ${CHAIN_RPC_URL} placeholders in run_command for fork PoCs."""
    is_fork = plan.get("fork") or result.get("fork")
    chain   = plan.get("fork_chain") or result.get("fork_chain", "")
    if not is_fork or not chain:
        return run_command
    rpc = resolve_fork_rpc(chain)
    if not rpc:
        print(f"  [warn] No RPC found for chain '{chain}'. Set {chain.upper()}_RPC_URL env var.")
        return run_command
    env_var = f"${{{chain.upper()}_RPC_URL}}"
    if env_var in run_command:
        run_command = run_command.replace(env_var, rpc)
    return run_command


def load_result(finding_id: str) -> dict:
    path = POC_DIR / f"{finding_id}_result.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def load_plan(finding_id: str) -> dict:
    path = POC_DIR / f"{finding_id}_plan.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def find_all_generated() -> list[str]:
    """Return all finding IDs that have a generated test."""
    ids = []
    for result_file in sorted(POC_DIR.glob("*_result.json")):
        result = json.loads(result_file.read_text())
        test_file = Path(result.get("test_file", ""))
        if test_file.exists():
            ids.append(result["finding_id"])
    return ids


def run_test(run_command: str, cwd: str | None = None, timeout: int = 120) -> tuple[int, str, str]:
    print(f"  Running: {run_command}")
    try:
        proc = subprocess.run(
            run_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout after {timeout}s"
    except FileNotFoundError as e:
        return -1, "", f"Command not found: {e}"


def determine_status(rc: int, stdout: str, stderr: str) -> tuple[str, bool]:
    import re
    # Rust: error[ENNN], Solidity/Forge: Error (NNNN): or Compiler run failed
    compile_error = bool(re.search(
        r'error\[E\d+\]|^error:|^Error\s*\(\d+\)|Compiler run failed',
        stderr + stdout, re.MULTILINE | re.IGNORECASE,
    ))
    if compile_error and rc != 0:
        return "compile_error", False
    assertion_hit = (
        "BUG CONFIRMED" in stdout
        or ("test poc_" in stdout and "ok" in stdout)
        or rc == 0
    )
    if rc == 0:
        return "proved" if assertion_hit else "inconclusive", assertion_hit
    return "failed", False


def update_result(finding_id: str, rc: int, stdout: str, stderr: str,
                  run_command: str, test_file: str = "") -> dict:
    status, assertion_hit = determine_status(rc, stdout, stderr)

    existing = load_result(finding_id)
    result = {
        **existing,
        "finding_id":    finding_id,
        "status":        status,
        "run_command":   run_command,
        "stdout_excerpt": stdout[:2000],
        "stderr_excerpt": stderr[:2000],
        "assertion_hit": assertion_hit,
        "generated_at":  datetime.now(timezone.utc).isoformat(),
    }

    (POC_DIR / f"{finding_id}_result.json").write_text(json.dumps(result, indent=2))

    # Append to results.jsonl
    with (POC_DIR / "results.jsonl").open("a") as fh:
        fh.write(json.dumps(result) + "\n")

    # ── viz: emit EXPLOIT_PROVED or EXPLOIT_FAILED ───────────────────────────
    try:
        from viz.event_emitter import emit as _viz_emit
        _evt = "EXPLOIT_PROVED" if status == "proved" else "EXPLOIT_FAILED"
        _viz_emit(_evt, source_agent="poc_runner", target_node_id=finding_id, payload={
            "status": status,
            "failure_reason": stderr[:400] if status != "proved" else None,
            "test_file": test_file,
            "assertion_hit": assertion_hit,
            "evidence_summary": f"PoC {status}" + (f" at rc={rc}" if status != "proved" else ""),
        })
    except Exception:
        pass

    # ── Hermes: emit poc_proved / poc_failed ─────────────────────────────────
    try:
        from scripts.emit_hermes_event import emit_hermes as _h_emit
        from audit_context import get_audit_meta as _get_meta
        _h_emit("poc_proved" if status == "proved" else "poc_failed", {
            "finding_id": finding_id,
            "status": status,
            "assertion_hit": assertion_hit,
            "failure_reason": stderr[:200] if status != "proved" else None,
            "audit_id": _get_meta().get("audit_id", ""),
        })
    except Exception:
        pass

    return result


def run_one(finding_id: str) -> dict:
    print(f"\n=== {finding_id} ===")
    result  = load_result(finding_id)
    plan    = load_plan(finding_id)

    test_file   = result.get("test_file", "")
    run_command = result.get("run_command") or plan.get("run_command", "")
    cwd         = result.get("cwd") or plan.get("cwd")
    timeout     = int(result.get("timeout", plan.get("timeout", 120)))

    if not test_file or not Path(test_file).exists():
        # Try to find it (Rust PoC default path)
        crate_dir = POCS_DIR / "k2" / finding_id
        for candidate in crate_dir.rglob("lib.rs"):
            test_file = str(candidate)
            break
        if not test_file:
            print(f"  [skip] No test file found for {finding_id}")
            return {}

    if not run_command:
        run_command = f"cargo test --manifest-path {POCS_DIR / 'k2' / finding_id / 'Cargo.toml'} -- --nocapture"

    run_command = resolve_run_command(run_command, plan, result)

    rc, stdout, stderr = run_test(run_command, cwd=cwd, timeout=timeout)
    result = update_result(finding_id, rc, stdout, stderr, run_command, test_file=test_file)

    status_icon = {"proved": "✓", "failed": "✗", "inconclusive": "?", "compile_error": "!"}.get(
        result["status"], "?"
    )
    print(f"  {status_icon} {result['status'].upper()}  (exit={rc})")
    if stdout:
        print(f"  stdout: {stdout[:200]}")
    if stderr and result["status"] == "compile_error":
        print(f"  stderr: {stderr[:300]}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Run PoC tests for audit findings")
    parser.add_argument("--finding-id", default=None)
    parser.add_argument("--repo",       default="contracts/2026-04-k2")
    parser.add_argument("--all",        action="store_true", help="Run all generated PoC tests")
    args = parser.parse_args()

    if args.all:
        finding_ids = find_all_generated()
        if not finding_ids:
            print("No generated PoC tests found.")
            return 0
        print(f"Running {len(finding_ids)} PoC tests...\n")
        results = [run_one(fid) for fid in finding_ids]

        proved   = sum(1 for r in results if r.get("status") == "proved")
        failed   = sum(1 for r in results if r.get("status") == "failed")
        errored  = sum(1 for r in results if r.get("status") == "compile_error")
        inconc   = sum(1 for r in results if r.get("status") == "inconclusive")

        print(f"\n{'='*50}")
        print(f"  Proved:         {proved}")
        print(f"  Inconclusive:   {inconc}")
        print(f"  Failed:         {failed}")
        print(f"  Compile errors: {errored}")

    elif args.finding_id:
        run_one(args.finding_id)
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
