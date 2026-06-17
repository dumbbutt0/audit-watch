#!/usr/bin/env python3
"""Stage 4 — freeze the blind audit result BEFORE any answer-key access."""
import json, hashlib, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,"scripts")
from audit_context import audit_path
NOW=datetime.now(timezone.utc).isoformat()
WS=Path(audit_path("output")).parent
SNAP=audit_path("output/eval_ready/pre_answer_key_snapshot"); SNAP.mkdir(parents=True,exist_ok=True)
ARTIFACTS=[
 "output/merged_findings.json","output/eval_ready/eval_findings.json",
 "output/eval_ready/eval_candidate_inventory.json","output/eval_ready/eval_duplicate_map.json",
 "output/eval_ready/eval_exclusions.json","output/coverage_manifest.json",
 "output/coverage_dispositions.json","output/coverage_gate.json","output/coverage_metrics.json",
 "output/confirm/reachability_analysis.json","output/confirm/confirm_gate.json","output/confirm/confirm_inventory.json",
 "scope/program_scope.json","scope/contract_source_manifest.json",
 "data/invariants/protocol_invariants.json","data/interactions/call_graph.json",
 "data/threads/promising_threads.jsonl","output/findings_deep_trace.json",
]
def sha256(p): return hashlib.sha256(p.read_bytes()).hexdigest()
entries=[]; missing=[]
for rel in ARTIFACTS:
    src=WS/rel
    if not src.exists(): missing.append(rel); continue
    dest=SNAP/rel.replace("/","__"); shutil.copy2(src,dest); st=src.stat()
    entries.append({"path":rel,"snapshot_copy":str(dest.relative_to(WS)),"sha256":sha256(src),
        "size":st.st_size,"mtime":datetime.fromtimestamp(st.st_mtime,timezone.utc).isoformat(),
        "frozen_at":NOW,"note":"frozen before answer-key access"})
(SNAP/"MANIFEST.json").write_text(json.dumps({"generated_at":NOW,
    "note":"frozen before answer-key access — blind audit result. Do not modify frozen findings after this point.",
    "answer_key_access_status_at_freeze":"not_accessed_before_freeze","file_count":len(entries),
    "missing":missing,"files":entries}, indent=2))
ps_path=audit_path("scope/program_scope.json"); ps=json.loads(ps_path.read_text())
ps["answer_key_access_status"]="freeze_complete_answer_key_not_yet_accessed"; ps["blind_freeze_at"]=NOW
ps_path.write_text(json.dumps(ps,indent=2))
print(f"FROZEN {len(entries)} artifacts; missing={missing}")
print("answer_key_access_status ->", ps["answer_key_access_status"])
