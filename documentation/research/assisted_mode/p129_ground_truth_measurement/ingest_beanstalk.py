#!/usr/bin/env python3
"""P129 — ingest beanstalk committed verdicts into ground_truth via the sanctioned single writer.

- Outcomes are TRANSCRIBED from committed eval artifacts (evals/beanstalk_finale/match_matrix.json +
  scorecard.json); no outcome is invented. evidence_class=platform_confirmed, recorded_by=contest_result.
- Targets beanstalk's eval dir via write_outcome(eval_dir=...) WITHOUT switching the active audit
  (same mechanism backfill_outcomes uses). Repo scripts are not modified.
- ADJACENT (ambiguous near-miss) findings present in merged_findings are routed to needs_human_review
  (no clean verdict to assert) — never guessed.
- beanstalk/data/triage was empty (eval ran via the independent path); we reconstruct submit/merged
  decisions ONLY for the verdicted findings, FAITHFULLY from merged_findings.json (= pipeline-promoted),
  so compute_metrics can resolve decisions instead of emitting a misleading 0.0.
"""
import json, sys
from pathlib import Path
ROOT = Path("/home/dummy/clones/audit-watch/smart-contract-auditor")
sys.path.insert(0, str(ROOT / "scripts"))
from ingest_ground_truth import write_outcome, _now

BEAN = ROOT / "audits" / "beanstalk-2024-05"
EVAL_DIR = BEAN / "data" / "evaluation"
TRIAGE_DIR = BEAN / "data" / "triage"
SRC = "evals/beanstalk_finale/match_matrix.json"
SRC2 = "evals/beanstalk_finale/scorecard.json"

# claimed severities pulled from merged_findings.json (the pipeline's own claim)
merged = {f["id"]: f for f in json.loads((BEAN / "output" / "merged_findings.json").read_text())["findings"]}

# (finding_id, outcome, gt_severity, evidence_class, source, evidence_summary)
VALID = [  # HIT/PARTIAL public findings -> accepted; gt_sev = top matched public bucket (INDICATIVE)
    ("US-001", "high",   "match_matrix: HIT (subs 251,323,327,330,444,447) — L2 migration mass-reissue"),
    ("AC-001", "high",   "match_matrix: HIT (sub 397) — auth boundary"),
    ("BSA-001","medium", "match_matrix: HIT (subs 68,186,303,478)"),
    ("EA-001", "high",   "match_matrix: HIT (8 subs) — economic/L2 migration"),
    ("FL-001", "high",   "match_matrix: HIT (subs 90,454,519)"),
    ("LG-001", "high",   "match_matrix: HIT (subs 224,411,412)"),
    ("SN-001", "high",   "match_matrix: HIT (sub 328)"),
    ("BSA-003","high",   "match_matrix: HIT (subs 324,325,328)"),
    ("CC-002", "high",   "match_matrix: HIT (subs 128,131)"),
    ("AC-003", "medium", "match_matrix: HIT (subs 37,228) — wrong typehash"),
    ("DS-003", "medium", "match_matrix: PARTIAL (subs 140,378,395)"),
    ("PC-001", "high",   "match_matrix: HIT (10 subs) — L2 migration cluster"),
]
INVALID = [  # scorecard pipeline_only_FP (in merged_findings)
    ("AR-001", "scorecard: pipeline_only_FP — speculative-reachability (most_wasteful_fp_source)"),
    ("EA-002", "scorecard: pipeline_only_FP — promoted lead with no awarded counterpart"),
]
DUP = [("AR-002", "medium", "match_matrix.merged_dups: AR-002 -> DS-003 (internal duplicate)")]
ADJACENT = [  # present in merged_findings, ambiguous near-miss -> needs_human_review
    ("AC-002", "match_matrix: ADJACENT (sub 320) — near-miss, human must decide HIT credit"),
    ("SG-001", "match_matrix: ADJACENT (sub 505) — near-miss, human must decide HIT credit"),
]

def rec(fid, outcome, sev, evidence, ecls="platform_confirmed"):
    f = merged.get(fid, {})
    return {
        "finding_id": fid, "source_audit": "beanstalk-2024-05",
        "title": f.get("title",""), "vuln_type": f.get("vuln_type",""),
        "claimed_severity": f.get("severity",""), "agent": f.get("_source_agent",""),
        "ground_truth_outcome": outcome, "ground_truth_severity": sev,
        "assumption_count": 0, "critical_assumptions": [], "rejection_reason": "",
        "evidence_class": ecls, "source_file": SRC, "evidence_summary": evidence,
        "confidence": 0.7, "recorded_by": "contest_result", "recorded_at": _now(),
    }

written = []; routed = []
for fid, sev, ev in VALID:
    ok, dest = write_outcome(rec(fid, "accepted", sev, ev), eval_dir=EVAL_DIR); written.append((fid,ok,dest))
for fid, ev in INVALID:
    ok, dest = write_outcome(rec(fid, "invalid", "invalid", ev), eval_dir=EVAL_DIR); written.append((fid,ok,dest))
for fid, sev, ev in DUP:
    r = rec(fid, "duplicate", sev, ev); r["duplicate_of_report"]="DS-003"
    ok, dest = write_outcome(r, eval_dir=EVAL_DIR); written.append((fid,ok,dest))
# ADJACENT -> needs_human_review: omit evidence_summary so the single writer routes it (honest: no verdict)
for fid, ev in ADJACENT:
    r = rec(fid, "escalated", "low", "", ecls=""); r["rejection_reason"]=ev
    ok, dest = write_outcome(r, eval_dir=EVAL_DIR); routed.append((fid,ok,dest))

# Faithful triage reconstruction (verdicted findings only): submit = promoted-and-verdicted; merged = the dup
TRIAGE_DIR.mkdir(parents=True, exist_ok=True)
submit_ids = [fid for fid,_,_ in VALID] + [fid for fid,_ in INVALID]
with (TRIAGE_DIR / "submit.jsonl").open("w") as fh:
    for fid in submit_ids:
        fh.write(json.dumps({"finding_id": fid, "triage_status": "submit",
            "_reconstructed_from": "merged_findings.json (pipeline-promoted); P129"}) + "\n")
with (TRIAGE_DIR / "merged.jsonl").open("w") as fh:
    fh.write(json.dumps({"finding_id": "AR-002", "triage_status": "merged",
        "_reconstructed_from": "match_matrix.merged_dups; P129"}) + "\n")

print("WRITTEN to ground_truth:")
for fid,ok,dest in written: print(f"  {fid:8} ok={ok} -> {Path(dest).name}")
print("ROUTED to needs_human_review:")
for fid,ok,dest in routed: print(f"  {fid:8} ok={ok} -> {Path(dest).name}")
gt = [l for l in (EVAL_DIR/'ground_truth.jsonl').read_text().splitlines() if l.strip()]
nh = (EVAL_DIR/'needs_human_review.jsonl')
nhn = len([l for l in nh.read_text().splitlines() if l.strip()]) if nh.exists() else 0
print(f"\nground_truth.jsonl: {len(gt)} records | needs_human_review.jsonl: {nhn} records")
print(f"submit.jsonl: {len(submit_ids)} | merged.jsonl: 1")
