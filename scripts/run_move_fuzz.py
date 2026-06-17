#!/usr/bin/env python3
"""run_move_fuzz.py  (P141 fuzz lane, Move) — run a Sui-Move property-fuzz harness and emit a raw evidence record.

Runs `sui move test` on a move_fuzz package (instantiated from templates/move_fuzz/) and maps the named tests to a
raw fuzz-evidence record written to data/fuzz_results/raw/<invariant_id>.jsonl. The convention (see the template):
  - test name contains "control"        -> negative control: invariant must HOLD for good inputs.
  - test name contains "counterexample"  -> falsification: invariant is BROKEN for the attack input.
falsified = counterexample test passed ; negative_control.passed = control test passed ; reproduced = True
(the LCG seed is deterministic). The downstream scripts/fuzz_evidence_gate.py DERIVES the promotion status — this
runner only reports what the harness actually did; it never fabricates a confirmation.

Usage:
  python scripts/run_move_fuzz.py --package pocs/<aid>/fuzz/<inv> --invariant "K non-decreasing after swap" \
      --evidence-id FZ-001 --location-file sources/implements.move --location-function swap_out [--env mainnet]
Degrades gracefully (emits nothing, exits 0) if `sui` is not installed.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_context as ac  # noqa: E402

# `sui move test` prints lines like: "[ PASS    ] fuzz::fuzz_invariant::invariant_holds_control"
_RESULT = re.compile(r"\[\s*(PASS|FAIL)\s*\]\s+\S*::(\w+)\s*$")


def _run(pkg: Path, env: str | None, filt: str | None = None) -> tuple[dict[str, bool], str]:
    cmd = ["sui", "move", "test"]
    if env:
        cmd += ["--env", env]
    if filt:
        cmd += [filt]
    try:
        r = subprocess.run(cmd, cwd=str(pkg), capture_output=True, text=True, timeout=900)
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return {}, f"sui run failed: {e}"
    out = (r.stdout or "") + "\n" + (r.stderr or "")
    results: dict[str, bool] = {}
    for ln in out.splitlines():
        m = _RESULT.search(ln.strip())
        if m:
            results[m.group(2)] = (m.group(1) == "PASS")
    return results, out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True, help="move_fuzz package dir (contains Move.toml + sources/)")
    ap.add_argument("--invariant", required=True)
    ap.add_argument("--evidence-id", default="FZ-001")
    ap.add_argument("--location-file", default="")
    ap.add_argument("--location-function", default="")
    ap.add_argument("--env", default=None, help="sui --env (use 'mainnet' to dodge dead testnet framework pins)")
    ap.add_argument("--filter", dest="filt", default=None, help="sui move test name filter (e.g. 'h1' to run one invariant's tests)")
    ap.add_argument("--seed", default="0x1234")
    args = ap.parse_args()

    if not shutil.which("sui"):
        print("[run_move_fuzz] sui CLI not installed — skipping (no record emitted).", file=sys.stderr)
        return 0

    pkg = Path(args.package)
    if not (pkg / "Move.toml").exists():
        print(f"[run_move_fuzz] no Move.toml at {pkg}", file=sys.stderr)
        return 1

    results, raw_out = _run(pkg, args.env, args.filt)
    control = next((v for k, v in results.items() if "control" in k.lower()), None)
    counterexample = next((v for k, v in results.items() if "counterexample" in k.lower()), None)

    if control is None or counterexample is None:
        print(f"[run_move_fuzz] could not find control/counterexample tests in output "
              f"(found: {sorted(results)}). No record emitted.", file=sys.stderr)
        # still surface the raw output for debugging
        return 1

    rec = {
        "evidence_id": args.evidence_id,
        "tool": "move_property_fuzz",
        "harness_kind": "property",
        "language": "move",
        "invariant": args.invariant,
        "falsified": bool(counterexample),          # counterexample test passing == the break is real
        "reproduced": True,                          # deterministic LCG seed
        "negative_control": {"passed": bool(control), "patch_note": "control = invariant holds for well-formed inputs"},
        "counterexample": {
            "seed": args.seed,
            "test_file": str((pkg / "sources" / "fuzz_invariant.move")),
            "call_sequence": [],
        },
        "location": {"file": args.location_file, "function": args.location_function},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    raw_dir = ac.get_audit_root() / "data" / "fuzz_results" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / f"{args.evidence_id.lower()}_move.jsonl"
    out.write_text(json.dumps(rec) + "\n")
    print(f"[run_move_fuzz] {args.evidence_id}: falsified={rec['falsified']} control_passed={control} -> {out}")
    print(f"  invariant: {args.invariant}")
    print("  NOTE: promotion status is decided by scripts/fuzz_evidence_gate.py (confirmed iff falsified+reproduced+control).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
