#!/usr/bin/env python3
"""P300 — submission filter (RESEARCH-ONLY, ADVISORY, UN-WIRED). The real-hunt precision gate.

Given a P294 verification record, label it: `submit` iff `validity_confirmed == True` (an EXECUTED exploit OR
logic-differential confirmation, the verifier's word) — else `needs_human` (setup_only / needs_execution / refuted /
not built / fabricated-without-a-real-pass). confirmed-FP ≈ 0 by proof. The filter LABELS only — it never submits,
sets severity, or touches confirm_gate/min_confirm_gate; a human submits.

Importable: filter_record(rec) -> {label, reason}; filter_many(records) -> summary.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

_STAMP = {"research_only": True, "is_gate": False, "emits_findings": False, "auto_submitted": False,
          "severity": None, "reportable": False, "submission_ready": False}


def filter_record(rec: dict) -> dict:
    """A record may `submit` ONLY if the verifier confirmed it by execution (validity_confirmed). Anything else,
    including a self-asserted status with no real pass, routes to human review."""
    confirmed = bool(rec.get("validity_confirmed"))
    status = rec.get("status")
    # defense-in-depth: even if validity_confirmed were set, require the confirmed status + (for exploit) a real run
    real = status in ("confirmed_by_execution", "confirmed_by_logic_differential")
    label = "submit" if (confirmed and real) else "needs_human"
    reason = ("executed " + ("exploit" if rec.get("attacker_verified") else "logic-differential")
              + " confirmation -> submit") if label == "submit" else \
             f"not an executed confirmation (status={status}) -> human review"
    return {"finding_id": rec.get("finding_id") or rec.get("awarded_id"), "label": label, "reason": reason,
            "validity_confirmed": confirmed, "status": status}


def filter_many(records: list) -> dict:
    rows = [filter_record(r) for r in records]
    submit = [r for r in rows if r["label"] == "submit"]
    # a submit-labelled record that is NOT a real executed confirmation would be a filter leak (must be 0)
    leaks = [r for r in submit if not (r["validity_confirmed"] and
             r["status"] in ("confirmed_by_execution", "confirmed_by_logic_differential"))]
    return dict(_STAMP, n=len(rows), submit=len(submit), needs_human=len(rows) - len(submit),
                submit_loci=[r["finding_id"] for r in submit], filter_leaks=len(leaks), rows=rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True, help="JSON file: list of verification records, or {records:[...]}")
    ap.add_argument("--out")
    a = ap.parse_args()
    d = json.loads(Path(a.records).read_text())
    recs = d if isinstance(d, list) else (d.get("records") or d.get("results") or [])
    out = filter_many(recs)
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=2))
    print(json.dumps({k: out[k] for k in ("n", "submit", "needs_human", "submit_loci", "filter_leaks")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
