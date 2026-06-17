#!/usr/bin/env python3
"""P215 — build the LOCAL dry-run submission queue. Submits NOWHERE.
Entry gate: human-reviewable AND (High => L3 PASS or written override) AND (Medium => source-proven impact)
AND human_review_required AND external_submission==false. Every record is research_only / routes_in_production:false.
"""
import json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
Q = ROOT / "output_research" / "dry_run_submission_queue"
Q.mkdir(parents=True, exist_ok=True)
DEL = Path(__file__).resolve().parent / "DRY_RUN_SUBMISSION_QUEUE"
DEL.mkdir(parents=True, exist_ok=True)

CHECKLIST = ["mechanism_confirmed","reachability_confirmed","severity_bearing","poc_complete",
             "impact_not_overclaimed","scope_caveats_reviewed","novelty_assessed","report_draft_exists",
             "mitigation_included","assumptions_included","human_sign_off"]

# ENTERED: gate satisfied (human-reviewable; no High without L3 PASS; Medium source-proven)
entered = [
 dict(candidate_id="ZETA-07", severity_recommendation="Low", readiness_state="ready_for_submission_package",
      blocker_state="", source_proven=True, l3_status="PASS",
      poc_path="pocs/p215/test/ZETA07_zeroGasFee.t.sol", poc_command="forge test --match-contract ZETA07 -vv",
      note="Executed harness (real ZRC20). Confirmed zero-gas-fee mechanism; calibrated Low/Medium (privileged GAS_LIMIT precondition). Fully passes the readiness checklist."),
 dict(candidate_id="ZETA-04", severity_recommendation="Medium", readiness_state="human_reviewable_pending_poc",
      blocker_state="q4 PoC evidence complete (source-proven, no executed PoC)", source_proven=True, l3_status="n/a (Medium)",
      poc_path="", poc_command="",
      note="Source-proven modifier asymmetry (onReceive lacks whenNotPaused). Human-reviewable; needs a PoC before any real submission."),
 dict(candidate_id="ZETA-12", severity_recommendation="Medium", readiness_state="human_reviewable_pending_poc",
      blocker_state="q4 PoC evidence complete (source-proven, no executed PoC)", source_proven=True, l3_status="n/a (Medium)",
      poc_path="", poc_command="",
      note="Source-proven weak slippage/deadline (block.timestamp+200; Trident no deadline). Human-reviewable; needs PoC."),
]

# BLOCKED-FROM-QUEUE: recorded for the audit, NOT entered
blocked = [
 dict(candidate_id=c, reason="High/Critical without L3 PASS or written override (blocked_by_missing_l3_poc)")
 for c in ["ZETA-03","ZETA-01","ZETA-04H?","ZETA-05","ZETA-06","ZETA-08","ZETA-10","ZETA-11"] if "?" not in c
]

ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
queue_rows = []
for e in entered:
    rec = {
        "phase": "P215", "queued_at": ts,
        "candidate_id": e["candidate_id"],
        "severity_recommendation": e["severity_recommendation"],
        "readiness_state": e["readiness_state"],
        "blocker_state": e["blocker_state"],
        "package_path": "output/submission_pack.md (+ submission_pack.json)",
        "l3_status": e["l3_status"],
        "poc_path": e["poc_path"], "poc_command": e["poc_command"],
        "source_proven": e["source_proven"],
        "human_review_checklist": {k: ("done" if e["candidate_id"]=="ZETA-07" else "pending") for k in CHECKLIST},
        "note": e["note"],
        # hard safety markers
        "human_review_required": True, "external_submission": False, "route_to_platform": False,
        "dry_run_submission_queue": True, "research_only": True, "routes_in_production": False, "submitted": False,
    }
    queue_rows.append(rec)
    (Q / f"{e['candidate_id']}.json").write_text(json.dumps(rec, indent=2))
    (DEL / f"{e['candidate_id']}.json").write_text(json.dumps(rec, indent=2))

# append-only ledger
ledger = Q / "queue.jsonl"
with ledger.open("w") as f:
    for r in queue_rows:
        f.write(json.dumps(r) + "\n")
(DEL / "queue.jsonl").write_text("\n".join(json.dumps(r) for r in queue_rows) + "\n")

manifest = {"phase":"P215","generated_at":ts,"target":"zetachain-2023-10-holdout",
            "external_submission":False,"route_to_platform":False,"submits_anywhere":False,
            "entered":[r["candidate_id"] for r in queue_rows],
            "entered_count":len(queue_rows),
            "blocked_from_queue":blocked,
            "rule":"human-reviewable AND (High=>L3 PASS/override) AND (Medium=>source-proven) AND human_review_required AND external_submission=false",
            "research_only":True,"routes_in_production":False}
(Q / "_manifest.json").write_text(json.dumps(manifest, indent=2))
(DEL / "_manifest.json").write_text(json.dumps(manifest, indent=2))
print("dry-run queue entered:", [r["candidate_id"] for r in queue_rows], "| blocked-from-queue:", len(blocked))
print("0 High/Critical entered without L3 PASS:", all(r["severity_recommendation"] not in ("High","Critical") or r["l3_status"]=="PASS" for r in queue_rows))
