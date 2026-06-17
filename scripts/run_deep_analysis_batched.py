#!/usr/bin/env python3
"""
run_deep_analysis_batched.py

Runs the deep invariant analysis pipeline on a list of individual contract
files, accumulating invariants across batches. Needed when rate limits
prevent processing the full contract directory in a single call.

Usage:
    python scripts/run_deep_analysis_batched.py --contracts <file1> [<file2> ...]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path

INVARIANTS_FILE = audit_path("data/invariants") / "protocol_invariants.json"
HIGH_SUSPICION_FILE = audit_path("data/invariants") / "high_suspicion.json"


def load_existing_invariants() -> list:
    try:
        return json.loads(INVARIANTS_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_invariants(invariants: list) -> None:
    INVARIANTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    INVARIANTS_FILE.write_text(json.dumps(invariants, indent=2, ensure_ascii=False))
    high = [i for i in invariants if i.get("suspicion_score", 0) >= 4]
    HIGH_SUSPICION_FILE.write_text(json.dumps(high, indent=2, ensure_ascii=False))
    print(f"  Cumulative invariants: {len(invariants)} total, {len(high)} high-suspicion")


def run_stage(cmd: list[str], label: str) -> bool:
    print(f"\n  Running {label}...")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contracts", nargs="+", required=True,
                        help="Contract files to analyze (one or more)")
    parser.add_argument("--delay", type=float, default=65.0,
                        help="Seconds to wait between batches (default: 65 to reset rate limit)")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    all_invariants: list = []

    print(f"Batched Deep Analysis — {len(args.contracts)} contract(s)")
    print(f"Rate-limit delay between calls: {args.delay}s\n")

    for i, contract in enumerate(args.contracts):
        cp = Path(contract)
        if not cp.exists():
            print(f"  SKIP: {contract} — not found")
            continue

        print(f"[{i+1}/{len(args.contracts)}] {cp.name}")

        # Stage 0a — extract invariants for this contract
        ok = run_stage(
            [sys.executable, str(root / "scripts" / "extract_invariants.py"),
             "--contract", str(cp)],
            f"extract_invariants on {cp.name}"
        )

        # Read what was written and accumulate
        try:
            new_invariants = json.loads(INVARIANTS_FILE.read_text())
            # Deduplicate by invariant name
            existing_names = {inv.get("name", "") for inv in all_invariants}
            added = [inv for inv in new_invariants if inv.get("name", "") not in existing_names]
            all_invariants.extend(added)
            print(f"  Added {len(added)} new invariants (total: {len(all_invariants)})")
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"  Could not read invariants from {cp.name}")

        # Save accumulated invariants after each batch
        if all_invariants:
            save_invariants(all_invariants)

        # Wait for rate limit to reset between contracts (skip after last)
        if i < len(args.contracts) - 1:
            print(f"  Waiting {args.delay}s for rate limit reset...")
            time.sleep(args.delay)

    print(f"\nBatch Stage 0a complete — {len(all_invariants)} total invariants")

    # Now run map_interactions and deep_trace on the first (largest) contract
    # since they build on the accumulated invariants already on disk
    print("\nRunning Stage 0b — Interaction Mapping (on first contract in list)...")
    first = args.contracts[0]
    run_stage(
        [sys.executable, str(root / "scripts" / "map_interactions.py"),
         "--contract", first],
        "map_interactions"
    )

    print("\nRunning Stage 0c — Deep Trace...")
    run_stage(
        [sys.executable, str(root / "scripts" / "deep_trace.py")],
        "deep_trace"
    )

    print("\nRunning Stage 0d — Thread Escalation...")
    run_stage(
        [sys.executable, str(root / "scripts" / "escalate_threads.py")],
        "escalate_threads"
    )

    high_count = len(load_existing_invariants())
    print(f"\nBatched Deep Analysis complete — {high_count} invariants in final set")
    return 0


if __name__ == "__main__":
    sys.exit(main())
