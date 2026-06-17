#!/usr/bin/env python3
"""P215 — register the 12 ZetaChain candidates into the research FUNNEL track so they surface on the dashboard's
/funnel, /findings and /candidates pages (which read documentation/research/funnel/funnel_records.json via
funnel.load_records() + findings_overview.load_overview()).

DATA-ONLY + ADDITIVE + IDEMPOTENT. Mirrors the existing `funnel-1` record schema. Every P215 record carries
research_only:true / routes_in_production:false / submission_ready:false and a not-ready human_readiness state.
Touches NO code (dashboard.py / findings_overview.py / funnel.py unchanged). Reversible: delete records whose
record_id starts with the P215 prefix. Re-running removes prior P215 records first (no duplicates).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
F = ROOT / "documentation/research/funnel/funnel_records.json"
DEL = Path(__file__).resolve().parent
REG = json.loads((DEL / "CANDIDATE_REGISTER.json").read_text())
PREFIX = "zetachain-2023-10:P215:"
SUBJECT = "ZetaChain 2023-10 (P215)"
L3DIR = ROOT / "output_research/l3_readiness"

SURFACE = {"CRITICAL_THREAD": 9, "HIGH_THREAD": 7, "MEDIUM_THREAD": 5}

# per-candidate funnel arc overlay (honest, from the P215 run + ANSWER_KEY_SCORECARD). conversion is a plain
# descriptive string (never the reportable constant); poc_status REPRODUCED only for the one executed harness.
# conversion ∈ {CLEAN_HIT,STRONG_PARTIAL,ADJACENT,REJECTED,ABSTAINED,NONE}; poc_status ∈
# {NOT_STARTED,IN_PROGRESS,REPRODUCED,PARTIAL_REPRO,NOT_REPRODUCED} (validated by funnel.py).
OV = {
 "ZETA-07": dict(conversion="ADJACENT", poc_status="REPRODUCED", blocker=None, source_false=False,
   poc_dir="pocs/p215", test_file="pocs/p215/test/ZETA07_zeroGasFee.t.sol",
   test_command="forge test --match-contract ZETA07 -vv",
   vulnerable_result="GAS_LIMIT=0 -> withdrawGasFee()==0 -> withdraw() pays zero gas fee (2/2 PASS, real ZRC20).",
   human_readiness="Executed on real ZRC20; calibrated LOW/MEDIUM (privileged GAS_LIMIT precondition). Not awarded in the official report. Human review: treat as QA hardening.",
   note_scoring="non-awarded (admin-misconfig QA)"),
 "ZETA-04": dict(conversion="CLEAN_HIT", poc_status="NOT_STARTED", blocker="blocked_by_missing_l3_poc", source_false=False,
   human_readiness="Mechanism = official H-13 EXACTLY (onReceive lacks whenNotPaused while onRevert has it). P215 rated Medium; should be HIGH. Needs executed PoC. NOT submission-ready.",
   note_scoring="HIT == official H-13 (High); SEVERITY_UNDER (rated Medium); NEEDS_HARNESS"),
 "ZETA-11": dict(conversion="STRONG_PARTIAL", poc_status="NOT_STARTED", blocker="blocked_by_missing_l3_poc", source_false=False,
   human_readiness="Same contract/function/impact as official H-10 (Trident getZetaFromToken DoS) but P215 flagged getPools()[0] validation; real bug = wrong exactInputSingle router method. Re-mechanism + raise to High. NOT submission-ready.",
   note_scoring="PARTIAL ~ official H-10 (High); WRONG_MECHANISM; SEVERITY_UNDER; NEEDS_HARNESS"),
 "ZETA-03": dict(conversion="ADJACENT", poc_status="NOT_STARTED", blocker="blocked_by_missing_l3_poc", source_false=False,
   human_readiness="Trust-root rotation (TSS/connector/ZetaNonEth) lacks timelock; privileged/centralization. Matches official QA[09]. Correctly calibrated LOW. NOT submission-ready as High.",
   note_scoring="HIT == official QA[09]; SEVERITY_MATCH (Low)"),
 "ZETA-02": dict(conversion="ADJACENT", poc_status="NOT_STARTED", blocker=None, source_false=False,
   human_readiness="zetaFee transfer not balance-checked (accounting drift). ~ official QA[05] fee divergence. QA-level. NOT submission-ready.",
   note_scoring="PARTIAL ~ official QA[05]"),
 "ZETA-09": dict(conversion="REJECTED", poc_status="NOT_REPRODUCED", blocker="rejected: by-design / no protocol impact", source_false=True,
   human_readiness="Rejected at triage with a disproof: a rogue ZetaConnectorZEVM instance harms only those who approve it; the canonical protocol is unaffected. Not in the answer key (TRUE_NEGATIVE).",
   note_scoring="TRUE_NEGATIVE (not awarded)"),
 "ZETA-12": dict(conversion="NONE", poc_status="NOT_STARTED", blocker=None, source_false=False,
   human_readiness="deadline=block.timestamp+200 / weak MEV slippage. QA-class; not awarded in the official report. NOT submission-ready.",
   note_scoring="non-awarded (MEV/deadline QA-class)"),
}
# default for the remaining High-ceiling NEEDS_HARNESS candidates (ZETA-01/05/06/08/10): no official match in scope.
DEFAULT = dict(conversion="NONE", poc_status="NOT_STARTED", blocker="blocked_by_missing_l3_poc",
   source_false=False, human_readiness="High-ceiling candidate blocked from High by L3 (no executed realized-impact PoC). NOT submission-ready.", note_scoring="no official match in Solidity scope; NEEDS_HARNESS")


def _l3(cid):
    p = L3DIR / f"{cid}.json"
    return json.loads(p.read_text()) if p.exists() else {}


def build_record(c):
    cid = c["id"]; ov = dict(DEFAULT); ov.update(OV.get(cid, {}))
    l3 = _l3(cid)
    rec = {
        "record_id": f"{PREFIX}{cid}:{c['contract']}.{c['function']}",
        "subject": SUBJECT,
        "phase_discovered": "P215",
        "finding_id": cid,
        "contract": c["contract"],
        "function": c["function"],
        "blind_rank": REG["candidates"].index(c) + 1,
        "surface_score": SURFACE.get(c["threat_ceiling"], 5),
        "conversion": ov["conversion"],
        "mechanism_correctness": ("partial" if "PARTIAL" in ov["conversion"] else
                                  ("refuted" if ov["conversion"] == "REFUTED" else "correct")),
        "severity_gate": "n/a",
        "severity_fp_before_gate": False,
        "severity_fp": False,
        "adversarial_result": "n/a",
        "safety": {"source_false": ov["source_false"], "unsupported_ready": False, "hard_fail": False},
        "control": False,
        "control_promoted_incorrectly": False,
        "impact": f"{c['title']}  [P215 scoring: {ov['note_scoring']}]",
        "poc": {
            "poc_status": ov["poc_status"],
            "poc_phase": "P215",
            "poc_artifact_dir": ov.get("poc_dir"),
            "test_file": ov.get("test_file"),
            "test_command": ov.get("test_command"),
            "vulnerable_result": ov.get("vulnerable_result"),
            "minimal_patch_validated": False,
            "source_chain_complete": ov["poc_status"] == "REPRODUCED",
            "unsupported_claims_present": False,
            "remaining_blockers": ([ov["blocker"]] if ov["blocker"] else []),
            "human_submission_ready": False,
        },
        "submission": {
            "submission_status": "NOT_STARTED",
            "duplicate_check_status": "PENDING",
            "scope_check_status": "PENDING",
            "severity_check_status": "PENDING",
            "final_human_gate": "PENDING",
        },
        "human_readiness": ov["human_readiness"],
        "blocker_reason": ov["blocker"],
        "source_refs": {
            "candidate_register": "documentation/research/assisted_mode/p215_full_funnel_rehearsal/CANDIDATE_REGISTER.json",
            "l3_record": (f"output_research/l3_readiness/{cid}.json" if l3 else None),
            "scorecard": "documentation/research/assisted_mode/p215_full_funnel_rehearsal/ANSWER_KEY_SCORECARD.md",
        },
        # explicit per-record safety stamps (user requirement)
        "research_only": True,
        "routes_in_production": False,
        "submission_ready": False,
        "l3_status": l3.get("l3_status"),
        "claimed_severity": c["claimed_severity"],
    }
    return rec


def main():
    doc = json.loads(F.read_text())
    findings = doc.get("findings", [])
    before = len(findings)
    # idempotent: drop any prior P215 records
    findings = [r for r in findings if not str(r.get("record_id", "")).startswith(PREFIX)]
    kept = len(findings)
    new = [build_record(c) for c in REG["candidates"]]
    findings.extend(new)
    doc["findings"] = findings
    # preserve top-level flags untouched (do not reorder/alter)
    F.write_text(json.dumps(doc, indent=1) + "\n")
    print(f"before={before} kept_non_p215={kept} added_p215={len(new)} total={len(findings)}")
    print("top-level flags:", {k: doc.get(k) for k in
          ["schema_version", "research_only", "review_only", "routes_in_production", "is_gate"]})


if __name__ == "__main__":
    main()
