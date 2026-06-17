#!/usr/bin/env python3
"""
write_eval_ready.py  (QuantAMM eval — workspace-local harness, Zaros pattern)

Deterministic, read-only on its inputs. The shared scripts/build_eval_inventory.py carries a
Beanstalk-specific hardcoded CLUSTERS/ID_TO_CLUSTER map, so — exactly as the Zaros eval did — this
per-eval script builds the eval-ready layer directly from THIS audit's merged findings + triage
verdicts. The 8 merged findings are already root-cause distinct (no duplicates among them), so the
eval candidate set == the merged set, one root cause each.

Outputs:
  output/eval_ready/eval_findings.json   blind root-cause findings (the eval scoring set)
  output/eval_ready/eval_findings.md
  output/eval_ready/final_scoring_set.json   union (== eval findings here; no separate layers)
  output/eval_ready/final_scoring_set.md
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from audit_context import audit_path  # noqa

OUT = audit_path("output") / "eval_ready"
OUT.mkdir(parents=True, exist_ok=True)

merged = json.loads((audit_path("output") / "merged_findings.json").read_text())["findings"]

# triage status per finding
def load_jsonl(p):
    if not p.exists(): return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]

tdir = audit_path("data/triage")
status = {}
for bucket in ("submit", "downgraded", "poc_required", "merged", "rejected"):
    for r in load_jsonl(tdir / f"{bucket}.jsonl"):
        status[r["finding_id"]] = (bucket, r.get("recommended_severity"))
for r in load_jsonl(audit_path("data") / "human_review_queue.jsonl"):
    status.setdefault(r.get("finding_id"), ("unresolved_invariant", r.get("recommended_severity")))

# classification mapping (eval semantics)
CLASS = {
    "submit": "confirmed_eval_finding",
    "downgraded": "partial_eval_finding",
    "poc_required": "confirmed_eval_finding",
    "unresolved_invariant": "partial_eval_finding",
    "merged": "duplicate_of_existing",
    "rejected": "false_positive",
}
EXCLUDE = {"duplicate_of_existing", "false_positive", "insufficient_evidence"}

eval_findings, scoring_rows = [], []
n = 0
for f in merged:
    fid = f.get("id")
    bucket, rec_sev = status.get(fid, ("downgraded", f.get("severity")))
    classification = CLASS.get(bucket, "partial_eval_finding")
    n += 1
    eid = f"EVAL-{n:03d}"
    rc = fid.lower()
    row = {
        "eval_id": eid,
        "root_cause_id": rc,
        "blind_finding_id": fid,
        "title": f.get("title", ""),
        "severity_ceiling": rec_sev or f.get("severity"),
        "confidence": f.get("confidence", ""),
        "classification": classification,
        "affected_contracts": [f.get("_contract", f.get("location", {}).get("file", ""))],
        "affected_functions": [f.get("location", {}).get("function", "")],
        "triage_bucket": bucket,
        "duplicate_of": None,
        "source_leads": [f.get("_source_agent", "")],
        "excluded": classification in EXCLUDE,
    }
    eval_findings.append(row)
    if not row["excluded"]:
        scoring_rows.append({
            "id": fid, "eval_id": eid, "layer": "eval_candidate", "title": row["title"],
            "severity": row["severity_ceiling"], "classification": classification,
            "contract": row["affected_contracts"][0], "function": row["affected_functions"][0],
            "root_cause_id": rc, "confidence": row["confidence"], "duplicate_of": None,
        })

(OUT / "eval_findings.json").write_text(json.dumps(
    {"audit": "quantamm-2024-12-eval", "eval_findings": eval_findings,
     "count": len(eval_findings), "included": len(scoring_rows)}, indent=2))
(OUT / "final_scoring_set.json").write_text(json.dumps(
    {"audit": "quantamm-2024-12-eval", "note": "root-cause deduped blind scoring set",
     "findings": scoring_rows, "count": len(scoring_rows)}, indent=2))

def md_table(rows):
    out = ["| eval_id | blind_id | sev | classification | contract.function | title |",
           "|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['eval_id']} | {r['blind_finding_id']} | {r['severity_ceiling']} | "
                   f"{r['classification']} | {r['affected_contracts'][0].split('/')[-1]}.{r['affected_functions'][0]} | {r['title'][:70]} |")
    return "\n".join(out)

(OUT / "eval_findings.md").write_text("# QuantAMM eval — root-cause findings (blind)\n\n" + md_table(eval_findings) + "\n")
(OUT / "final_scoring_set.md").write_text("# QuantAMM eval — final scoring set (frozen pre-answer-key)\n\n" + md_table(eval_findings) + "\n")

print(f"[ok] eval_findings: {len(eval_findings)}  included(scoring): {len(scoring_rows)}  excluded: {len(eval_findings)-len(scoring_rows)}")
for r in eval_findings:
    print(f"   {r['eval_id']} {r['blind_finding_id']:8s} {r['severity_ceiling']:7s} {r['classification']:24s} {r['title'][:55]}")
