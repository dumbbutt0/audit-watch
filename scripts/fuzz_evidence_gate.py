#!/usr/bin/env python3
"""fuzz_evidence_gate.py  (P141) — the fuzz-lane false-positive guard.

Normalizes every deep-harness-fuzz signal into data/fuzz_results/divergences.jsonl and DERIVES a promotion
status for each. This is the precision protection that sits BEFORE the existing FP gauntlet: only signals whose
CAUSE is confirmed (reproduced AND the harness/oracle ruled out) are ever exposed to the
agents/fuzz_attacker_synthesis.md specialist. A harness/oracle artifact can therefore never manufacture a finding.

Status is DERIVED here (fail-closed) from the evidence, never trusted from the raw input:
  held            -> the invariant held / no divergence (a legitimate negative result; never a finding)
  confirmed        -> falsified AND reproduced AND artifact_ruled_out  (the ONLY status promoted)
  harness_artifact -> falsified but the harness/oracle is the cause (differential tie-break sides with the SUT,
                      or a property negative-control FAILED i.e. the property itself is ill-formed) -> rejected
  unreproduced     -> falsified but not deterministically reproduced, or cause not yet ruled out -> held back

artifact_ruled_out is computed, not trusted:
  differential : tie_break.agrees_with == 'reference'  (the third oracle says the SUT is wrong, not the harness)
  property     : negative_control.passed == True       (the property HOLDS under a minimal correctness patch /
                 on a reference impl, proving the property + harness are well-formed)

Raw inputs (any may be absent):
  data/fuzz_results/raw/*.jsonl        -> move_property_fuzz / aurora_evm_difffuzz / foundry_invariant runners
  data/threads/fuzzing_threads.jsonl   -> Echidna falsifications (generate_fuzzing_harness.py)

Read-only on source; deterministic; no LLM.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_context as ac  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def _policy() -> dict:
    try:
        p = json.loads((ROOT / "config" / "agent_policy.json").read_text())
        return p.get("fuzz_synthesis", {}) or {}
    except Exception:
        return {}


def _raw_records(adir: Path) -> list[dict]:
    """Collect raw harness emissions from all known sources, tagged with their tool."""
    out: list[dict] = []
    raw_dir = adir / "data" / "fuzz_results" / "raw"
    if raw_dir.exists():
        for p in sorted(raw_dir.glob("*.jsonl")):
            for ln in p.read_text().splitlines():
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    out.append(json.loads(ln))
                except Exception:
                    continue
        for p in sorted(raw_dir.glob("*.json")):
            try:
                d = json.loads(p.read_text())
            except Exception:
                continue
            out.extend(d if isinstance(d, list) else [d])
    # Echidna falsified-invariant threads
    threads = adir / "data" / "threads" / "fuzzing_threads.jsonl"
    if threads.exists():
        for ln in threads.read_text().splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
                r.setdefault("tool", "echidna")
                r.setdefault("harness_kind", "property")
                r.setdefault("falsified", True)  # a thread is emitted only on a falsified property
                out.append(r)
            except Exception:
                continue
    return out


def _derive_artifact_ruled_out(rec: dict) -> bool:
    kind = rec.get("harness_kind", "property")
    if kind == "differential":
        return (rec.get("tie_break") or {}).get("agrees_with") == "reference"
    return bool((rec.get("negative_control") or {}).get("passed"))


def _derive_status(rec: dict) -> str:
    if not rec.get("falsified", False):
        return "held"
    reproduced = bool(rec.get("reproduced", False))
    artifact_ruled_out = _derive_artifact_ruled_out(rec)
    if reproduced and artifact_ruled_out:
        return "confirmed"
    # explicit harness-cause: differential oracle sides with the SUT, or property negative-control failed
    kind = rec.get("harness_kind", "property")
    if kind == "differential" and (rec.get("tie_break") or {}).get("agrees_with") in ("sut", "neither"):
        return "harness_artifact"
    nc = rec.get("negative_control")
    if kind == "property" and isinstance(nc, dict) and nc.get("passed") is False:
        return "harness_artifact"
    return "unreproduced"


def normalize(adir: Path) -> list[dict]:
    raws = _raw_records(adir)
    norm: list[dict] = []
    for i, r in enumerate(raws, 1):
        status = _derive_status(r)
        norm.append({
            "evidence_id": r.get("evidence_id") or f"FZ-{i:03d}",
            "tool": r.get("tool", "other"),
            "harness_kind": r.get("harness_kind", "property"),
            "language": r.get("language"),
            "invariant": r.get("invariant", ""),
            "falsified": bool(r.get("falsified", False)),
            "reproduced": bool(r.get("reproduced", False)),
            "artifact_ruled_out": _derive_artifact_ruled_out(r),
            "status": status,
            "tie_break": r.get("tie_break"),
            "negative_control": r.get("negative_control"),
            "counterexample": r.get("counterexample"),
            "location": r.get("location"),
            "created_at": r.get("created_at"),
        })
    return norm


def confirmed_evidence(adir: Path | None = None) -> list[dict]:
    """Importable accessor: the ONLY records the synthesis specialist may consume."""
    adir = adir or ac.get_audit_root()
    div = adir / "data" / "fuzz_results" / "divergences.jsonl"
    if not div.exists():
        return []
    out = []
    for ln in div.read_text().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except Exception:
            continue
        if r.get("status") == "confirmed":
            out.append(r)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Normalize + cause-confirm harness-fuzz signals (the fuzz-lane FP guard).")
    ap.add_argument("--summary", action="store_true", help="print status counts only")
    ap.add_argument("--print-confirmed", action="store_true", help="print the confirmed records (json)")
    args = ap.parse_args()

    pol = _policy()
    if not pol.get("enabled", True):
        print("[fuzz_evidence_gate] fuzz_synthesis disabled in config/agent_policy.json — no-op.")
        return 0

    adir = ac.get_audit_root()
    norm = normalize(adir)
    out_dir = adir / "data" / "fuzz_results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "divergences.jsonl"
    out.write_text("".join(json.dumps(r) + "\n" for r in norm))

    counts: dict[str, int] = {}
    for r in norm:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    confirmed = counts.get("confirmed", 0)
    print(f"[fuzz_evidence_gate] {len(norm)} signal(s) -> {out}")
    print(f"  status: " + (", ".join(f"{k}={v}" for k, v in sorted(counts.items())) or "(none)"))
    if pol.get("require_cause_confirmation", True):
        print(f"  PROMOTED to synthesis (status=confirmed): {confirmed}"
              f"  [require_cause_confirmation=true — only these reach agents/fuzz_attacker_synthesis.md]")
    if args.print_confirmed:
        print(json.dumps([r for r in norm if r["status"] == "confirmed"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
