#!/usr/bin/env python3
"""P211 — read-only E2E rehearsal driver for the dark L3 readiness gate.

Drives the REAL P210 wired functions (no reimplementation): submission_readiness_review.evaluate / l3_evaluate /
detail_overlay / record_review, and the dashboard's L3 panel computation path. Toggles AUDITWATCH_L3_READINESS
in-process only. Submits/routes nothing; never persists the flag to config. Prints a JSON report.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
import submission_readiness_review as srr  # noqa: E402

# decent candidate fixtures: (candidate_id, severity_target). DEC-STATIC has NO l3 record on disk -> fail-closed.
CANDS = [
    ("DEC-H-01", "High"),     # genuine High, L3 PASS on disk
    ("DEC-M-03", "High"),     # awarded Medium / blind-High ceiling, L3 FAIL on disk -> should block as High
    ("DEC-M-03", "Medium"),   # same finding as a Medium target -> L3 not applicable
    ("DEC-STATIC", "High"),   # High target, no L3 record -> fail-closed
]

GOOD_ANS = lambda sev: {
    "mechanism_confirmed": "yes", "reachability_confirmed": "yes", "severity_bearing": "yes",
    "poc_complete": "yes", "impact_not_overclaimed": "yes", "severity_recommendation": sev,
    "scope_caveats_reviewed": "yes", "novelty": "novelty_clear", "report_draft_exists": "yes",
    "mitigation_included": "yes", "assumptions_included": "yes", "notes": "rehearsal",
}
GOOD_FACTS = lambda cid: {"reportable": True, "mechanism_confirmed": True, "attacker_reachable": True,
                          "severity_bearing": True, "candidate_id": cid}


def run(flag: bool):
    if flag:
        os.environ["AUDITWATCH_L3_READINESS"] = "1"
    else:
        os.environ.pop("AUDITWATCH_L3_READINESS", None)
    rows = []
    for cid, sev in CANDS:
        eligible, failed = srr.evaluate(GOOD_ANS(sev), GOOD_FACTS(cid))
        l3_block = [f for f in failed if f.startswith("blocked_by_missing_l3_poc")]
        # dashboard L3 panel path (mirrors dashboard.py guard)
        panel = None
        if os.environ.get("AUDITWATCH_L3_READINESS") in ("1", "true", "True", "yes", "on"):
            panel = srr.l3_evaluate(srr._load_l3_record(cid), sev)
        rows.append({
            "candidate_id": cid, "severity_target": sev, "eligible": eligible,
            "l3_blocker": (l3_block[0] if l3_block else None),
            "dashboard_l3_present": panel is not None,
            "dashboard_l3_readonly": (panel is None or (panel.get("research_only") is True and panel.get("routing_allowed") is False)),
            "high_promotion_allowed": (panel.get("high_promotion_allowed") if panel else None),
        })
    return {"flag": flag, "rows": rows}


def main():
    report = {"flag_off": run(False), "flag_on": run(True)}
    os.environ.pop("AUDITWATCH_L3_READINESS", None)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
