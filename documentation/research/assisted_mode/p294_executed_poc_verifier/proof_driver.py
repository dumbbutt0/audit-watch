#!/usr/bin/env python3
"""P294 proof driver (RESEARCH-ONLY, ADVISORY; not a frozen module, not wired).

Runs the executed-PoC verifier over the proof set with REAL forge executions and emits the phase outputs.
The verdict for each candidate is derived from an actual `forge test` run — no self-asserted status is trusted.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts/research"))
import executed_poc_verifier as epv  # noqa: E402

OUT = Path(__file__).resolve().parent / "outputs"

# (poc_dir, finding_id, audit_id, awarded?) — awarded loci have an entry in the corpus ground_truth answer keys.
PROOF_SET = [
    ("pocs/p286", "blackhole-M-04-claim_many", "blackhole-2025-05-eval", True),
    ("pocs/p294/salty_increaseUserShare", "salty-H-increaseUserShare-first-depositor", "salty-2024-01-holdout", True),
    ("pocs/p290/salty-2024-01-holdout/Pools_deposit", "salty-Pools-deposit-callback", "salty-2024-01-holdout", False),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for rel, fid, aud, awarded in PROOF_SET:
        rec = epv.verify_poc(ROOT / rel, audit_id=aud, finding_id=fid)
        rec["awarded_locus"] = awarded
        records.append(rec)

    confirmed = [r for r in records if r["attacker_verified"] and r["status"] == "confirmed_by_execution"]
    refused = [r for r in records if not r["attacker_verified"]]
    # confirmed-FP = a confirmed record whose locus is NOT an awarded bug (a false confirmation). Must be 0.
    confirmed_fp = [r for r in confirmed if not r.get("awarded_locus")]
    awarded_confirmed = [r for r in confirmed if r.get("awarded_locus")]

    (OUT / "verification_records.json").write_text(json.dumps(
        {"research_only": True, "is_gate": False, "auto_submitted": False, "records": records}, indent=2))
    (OUT / "recall_of_confirmed.json").write_text(json.dumps({
        "research_only": True, "severity": None,
        "confirmed_by_execution": [r["finding_id"] for r in confirmed],
        "awarded_loci_confirmed": [r["finding_id"] for r in awarded_confirmed],
        "refused_not_confirmed": [r["finding_id"] for r in refused],
        "confirmed_false_positive_count": len(confirmed_fp)}, indent=2))
    (OUT / "guard_report.json").write_text(json.dumps({
        "module": "executed_poc_verifier", "research_only": True, "is_gate": False, "emits_findings": False,
        "auto_submitted": False, "severity": None, "reportable": False, "submission_ready": False,
        "checks": {"awarded_loci_confirmed_by_execution": len(awarded_confirmed),
                   "false_hypothesis_refused": len(refused),
                   "confirmed_false_positive_count": len(confirmed_fp),
                   "every_confirmation_has_a_real_log": all(
                       any(x.get("passed") and x.get("log_ref") for x in r["runs"]) for r in confirmed)}}, indent=2))
    print(json.dumps({
        "awarded_confirmed": [r["finding_id"] for r in awarded_confirmed],
        "refused": [r["finding_id"] for r in refused],
        "confirmed_FP": len(confirmed_fp)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
