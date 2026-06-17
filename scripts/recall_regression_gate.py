#!/usr/bin/env python3
"""Recall Lab — regression guard.

Protects previously-caught findings: no prompt/config change may turn a TRAINING catch
(label in {STRONG, SAME_AREA, SUBSYSTEM_ONLY}) into a MISSED. This is the "don't break what we already catch"
gate for the recall lever (specialist prompt edits).

  python scripts/recall_regression_gate.py --snapshot   # capture current training catches as the baseline
  python scripts/recall_regression_gate.py              # check current adjudication vs baseline; exit 1 on regression

The baseline (evals/recall_baseline.json) is the protected set. The check re-reads each project's current
adjudication.json (which is regenerated from the cold pass after a prompt change + re-adjudication) and fails
if any baseline catch is no longer recalled. New catches are reported as improvements (non-blocking).
Mirrors the safety discipline of auto_promote_learning.is_recall_safe (a change is recall-safe iff it drops
no known catch); here the oracle is the persisted adjudication rather than the FP rule check.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "evals" / "corpus.json"
BASELINE = ROOT / "evals" / "recall_baseline.json"
RECALLED = {"STRONG", "SAME_AREA", "SUBSYSTEM_ONLY"}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _training_ids() -> list[str]:
    c = json.loads(CORPUS.read_text())
    return [r["id"] for r in c["sets"].get("training", []) if r.get("scoreable")]


# auto-heuristic / scaffold labels are NOT human-confirmed; never protect them as catches (they could lock in
# a false positive or cause a spurious regression). Only human/seed adjudications are protected.
_UNCONFIRMED_SRC = {"auto-heuristic", "scaffold"}


def _labels(audit_id: str, confirmed_only: bool = False) -> dict[str, str]:
    p = ROOT / "audits" / audit_id / "output" / "eval_ready" / "adjudication.json"
    if not p.exists():
        return {}
    out = {}
    for r in json.loads(p.read_text()).get("awarded", []):
        if confirmed_only and r.get("source") in _UNCONFIRMED_SRC:
            continue
        out[r["id"]] = r["label"]
    return out


def snapshot() -> dict:
    catches = {}
    for aid in _training_ids():
        labs = _labels(aid, confirmed_only=True)  # protect only human/seed catches
        caught = {fid: lab for fid, lab in labs.items() if lab in RECALLED}
        if caught:
            catches[aid] = caught
    doc = {"generated_at": _now(), "protected_catches": catches,
           "total": sum(len(v) for v in catches.values())}
    BASELINE.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"snapshot: {doc['total']} protected training catches across {len(catches)} projects -> "
          f"{BASELINE.relative_to(ROOT)}")
    return doc


def check() -> int:
    if not BASELINE.exists():
        print("no baseline — run --snapshot first", file=sys.stderr)
        return 2
    base = json.loads(BASELINE.read_text())["protected_catches"]
    regressions = []
    improvements = []
    for aid, caught in base.items():
        cur = _labels(aid)
        for fid, old_label in caught.items():
            now = cur.get(fid, "MISSING_FROM_ADJUDICATION")
            if now not in RECALLED:
                regressions.append((aid, fid, old_label, now))
    # improvements: current CONFIRMED (human/seed) catches not yet protected (ignore unconfirmed heuristic)
    for aid in _training_ids():
        for fid, lab in _labels(aid, confirmed_only=True).items():
            if lab in RECALLED and fid not in base.get(aid, {}):
                improvements.append((aid, fid, lab))

    if improvements:
        print(f"+ {len(improvements)} new catch(es) since baseline (re-snapshot to lock them in):")
        for aid, fid, lab in improvements[:20]:
            print(f"    + {aid} {fid} -> {lab}")
    if regressions:
        print(f"\nFAIL: {len(regressions)} regression(s) — previously-caught findings now MISSED:")
        for aid, fid, old, now in regressions:
            print(f"    ! {aid} {fid}: {old} -> {now}")
        return 1
    print(f"\nPASS: all {sum(len(v) for v in base.values())} protected training catches still recalled.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", action="store_true", help="capture current training catches as baseline")
    args = ap.parse_args()
    if args.snapshot:
        snapshot()
        return 0
    return check()


if __name__ == "__main__":
    sys.exit(main())
