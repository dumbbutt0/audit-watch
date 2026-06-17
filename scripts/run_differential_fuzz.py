#!/usr/bin/env python3
"""run_differential_fuzz.py  (P141 fuzz lane, EVM-core) — run the differential EVM harness and normalize its
divergences into raw fuzz-evidence records, with a geth tie-break that decides artifact-vs-bug.

The differential harness (default: ~/clones/aurora-evm-difffuzz) runs a generated case through the system-under-
test (e.g. aurora-evm) and a reference (revm) and flags gas/state/status divergences. A divergence alone is NOT a
finding: it may be a harness/env-mapping artifact. This runner attaches the THIRD-implementation tie-break
(geth `evm t8n`) result so scripts/fuzz_evidence_gate.py can decide:
    tie_break.agrees_with == "reference"  -> the SUT is wrong  -> confirmed (after reproduce)
    tie_break.agrees_with == "sut"/"neither" -> harness/reference artifact -> harness_artifact (rejected)

The harness is expected to emit a JSON-lines divergence file (one object per divergence) via its own
`--json-out` mode; each object should carry: seed, divergence axis/message, and (when a tie-break was run)
tie_break.agrees_with. This script reads that file, attaches metadata, and writes
data/fuzz_results/raw/<run>_diff.jsonl. It does NOT itself run geth; the harness/operator supplies the tie-break
result (mirrors the Aurora TRIAGE.md discipline: rule out the harness cause FIRST).

Usage:
  python scripts/run_differential_fuzz.py --divergences /path/to/harness_divergences.jsonl --language evm
  python scripts/run_differential_fuzz.py --harness ~/clones/aurora-evm-difffuzz --run   # if the harness supports --json-out
Degrades gracefully (exits 0, no record) when no divergences/harness are available.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_context as ac  # noqa: E402


def _load_divergences(path: Path) -> list[dict]:
    out = []
    for ln in path.read_text().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except Exception:
            continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--divergences", help="JSONL file of raw divergences emitted by the harness (--json-out)")
    ap.add_argument("--harness", help="harness workspace dir (e.g. ~/clones/aurora-evm-difffuzz)")
    ap.add_argument("--run", action="store_true", help="run the harness's emitter before reading (needs --json-out support)")
    ap.add_argument("--language", default="evm")
    ap.add_argument("--out-name", default="diff")
    args = ap.parse_args()

    div_path = Path(args.divergences).expanduser() if args.divergences else None

    if args.run and args.harness:
        hp = Path(args.harness).expanduser()
        emitted = hp / "fuzz_divergences.jsonl"
        try:
            subprocess.run(["cargo", "test", "randomized_differential_sweep", "--", "--nocapture"],
                           cwd=str(hp), capture_output=True, text=True, timeout=1800)
        except Exception as e:
            print(f"[run_differential_fuzz] harness run failed: {e}", file=sys.stderr)
        if emitted.exists():
            div_path = emitted

    if not div_path or not div_path.exists():
        print("[run_differential_fuzz] no divergence file available — skipping (no record emitted).", file=sys.stderr)
        return 0

    raws = _load_divergences(div_path)
    recs = []
    for i, d in enumerate(raws, 1):
        tb = d.get("tie_break") or {}
        recs.append({
            "evidence_id": d.get("evidence_id") or f"FZ-D{i:03d}",
            "tool": "aurora_evm_difffuzz",
            "harness_kind": "differential",
            "language": args.language,
            "invariant": d.get("message") or d.get("axis") or "SUT == reference (consensus/gas)",
            "falsified": True,
            "reproduced": bool(d.get("reproduced", d.get("seed") is not None)),
            "tie_break": {"oracle": tb.get("oracle", "geth evm t8n"), "agrees_with": tb.get("agrees_with")},
            "counterexample": {"seed": str(d.get("seed", "")), "trace_excerpt": d.get("message", "")},
            "location": d.get("location"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    raw_dir = ac.get_audit_root() / "data" / "fuzz_results" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / f"{args.out_name}_diff.jsonl"
    out.write_text("".join(json.dumps(r) + "\n" for r in recs))
    print(f"[run_differential_fuzz] {len(recs)} divergence(s) -> {out}")
    print("  NOTE: a divergence is promoted ONLY if its geth tie-break agrees_with=='reference' (geth says the SUT is wrong).")
    print("        Run scripts/fuzz_evidence_gate.py to derive the confirmed set.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
