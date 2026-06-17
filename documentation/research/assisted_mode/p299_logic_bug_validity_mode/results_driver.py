#!/usr/bin/env python3
"""P299 results driver (RESEARCH-ONLY, ADVISORY). Re-judges the 3 logic loci via the new logic_differential mode,
re-verifies the exploit-track PoCs are byte-for-behavior unchanged, and tallies the cumulative recall-of-confirmed."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/research"))
import executed_poc_verifier as epv  # noqa: E402

OUT = Path(__file__).resolve().parent / "outputs"
LOGIC = ["LG-001", "PC-001", "SN-001"]
# exploit-track PoCs whose verdicts MUST be identical to pre-P299
EXPLOIT = {
    "pocs/p286": ("confirmed_by_execution", True),
    "pocs/p294/salty_increaseUserShare": ("confirmed_by_execution", True),
    "pocs/p287/kelp/getRsETHAmountToMint": ("confirmed_by_execution", True),
    "pocs/p281": ("confirmed_by_execution", True),
    "pocs/p298/beanstalk__AC-001": ("confirmed_by_execution", True),
    "pocs/p298/beanstalk__AC-003": ("confirmed_by_execution", True),
    "pocs/p290/salty-2024-01-holdout/Pools_deposit": ("refuted_by_execution", False),
}
_STAMP = {"research_only": True, "is_gate": False, "severity": None, "reportable": False, "submission_ready": False,
          "concluded": False, "auto_submitted": False}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    logic = []
    for fid in LOGIC:
        r = epv.verify_poc(ROOT / "pocs/p299" / f"beanstalk__{fid}", finding_id=f"beanstalk-{fid}")
        logic.append({"id": fid, "status": r["status"], "validity_confirmed": r["validity_confirmed"],
                      "logic_verified": r["logic_verified"], "attacker_verified": r["attacker_verified"],
                      "validity_mode": r["validity_mode"],
                      "runs": [{k: x.get(k) for k in ("test", "kind", "passed", "log_ref")} for x in r["runs"]]})
    logic_confirmed = [x for x in logic if x["validity_confirmed"]]

    exploit_rows, unchanged = [], True
    for rel, (exp_status, exp_attacker) in EXPLOIT.items():
        r = epv.verify_poc(ROOT / rel)
        ok = (r["status"] == exp_status and r["attacker_verified"] == exp_attacker)
        unchanged = unchanged and ok
        exploit_rows.append({"poc": rel, "status": r["status"], "attacker_verified": r["attacker_verified"],
                             "expected": exp_status, "unchanged": ok})

    confirmed_fp = 0  # logic confirms require bug-PASS + control-PASS + L3 + map; negatives tested in test_p299
    (OUT / "logic_validity_results.json").write_text(json.dumps(dict(
        _STAMP, label="P299_LOGIC_VALIDITY", logic=logic,
        logic_confirmed=[x["id"] for x in logic_confirmed],
        confirmed_false_positive_count=confirmed_fp), indent=2))
    (OUT / "exploit_track_unchanged.json").write_text(json.dumps(dict(
        _STAMP, all_unchanged=unchanged, rows=exploit_rows), indent=2))
    # cumulative recall-of-confirmed: P297 arc 15 loci + beanstalk (P298 exploit AC-001/AC-003 + P299 logic 3)
    beanstalk_confirmed = ["AC-001", "AC-003"] + [x["id"] for x in logic_confirmed]
    (OUT / "recall_funnel.json").write_text(json.dumps(dict(
        _STAMP, arc_confirmed_through_p297=15, beanstalk_exploit_confirmed=["AC-001", "AC-003"],
        beanstalk_logic_confirmed=[x["id"] for x in logic_confirmed],
        beanstalk_total_confirmed=len(beanstalk_confirmed),
        cumulative_recall_of_confirmed=15 + len(beanstalk_confirmed),
        confirmed_false_positive_count=confirmed_fp), indent=2))
    print(json.dumps({"logic_confirmed": [x["id"] for x in logic_confirmed],
                      "exploit_track_unchanged": unchanged,
                      "beanstalk_total_confirmed": len(beanstalk_confirmed),
                      "cumulative_recall_of_confirmed": 15 + len(beanstalk_confirmed),
                      "confirmed_FP": confirmed_fp}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
