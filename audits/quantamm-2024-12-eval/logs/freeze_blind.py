#!/usr/bin/env python3
"""
freeze_blind.py (QuantAMM eval) — snapshot + sha256 every blind artifact BEFORE answer-key access.
Zaros-pattern, deterministic. Copies into output/pre_answer_key_snapshot/ and writes MANIFEST.json.
After this runs, scoring artifacts are immutable; integrity is re-verified post-answer-key.
"""
import json, hashlib, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from audit_context import audit_path  # noqa

ROOT = audit_path("")  # audit root
OUT = audit_path("output")
SNAP = OUT / "pre_answer_key_snapshot"
SNAP.mkdir(parents=True, exist_ok=True)

# (relative-to-audit-root path) list of blind artifacts to freeze
TARGETS = [
    "output/merged_findings.json",
    "output/eval_ready/eval_findings.json",
    "output/eval_ready/eval_findings.md",
    "output/eval_ready/final_scoring_set.json",
    "output/eval_ready/final_scoring_set.md",
    "output/coverage_manifest.json",
    "output/coverage_dispositions.json",
    "output/coverage_gate.json",
    "output/coverage_metrics.json",
    "output/min_confirm_gate.json",
    "output/review_gate.md",
    "output/status.json",
    "output/static.json",
    # triage buckets
    "data/triage/submit.jsonl",
    "data/triage/downgraded.jsonl",
    "data/triage/rejected.jsonl",
    "data/triage/_decisions.json",
    "data/triage/human_review_queue.jsonl",
    # confirm artifacts
    "output/confirm/confirm_inventory.json",
    "output/confirm/reachability_analysis.json",
    "output/confirm/confirm_gate.json",
    # lens audits
    "output/cross_chain_constants_audit.json",
    "output/token_standard_audit.json",
    "output/units_invariant_audit.json",
    "output/migration_flow_audit.json",
    "output/griefing_dos_audit.json",
    "output/defi_accounting_audit.json",
    "output/getter_state_audit.json",
    "output/silo_stalk_audit.json",
    # deep analysis
    "output/findings_deep_trace.json",
    "data/invariants/protocol_invariants.json",
    "data/interactions/call_graph.json",
    "data/threads/promising_threads.jsonl",
    # scope + plan
    "scope/program_scope.json",
    "scope/scope_reconstruction.md",
    "eval_plan.md",
    "output/pre_audit_snapshot/build_status.json",
]

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()

now = datetime.now(timezone.utc).isoformat()
entries, missing = [], []
for rel in TARGETS:
    src = ROOT / rel
    if not src.exists():
        missing.append(rel); continue
    dest_name = rel.replace("/", "__")
    dest = SNAP / dest_name
    shutil.copy2(src, dest)
    st = src.stat()
    entries.append({
        "path": rel,
        "snapshot_copy": f"output/pre_answer_key_snapshot/{dest_name}",
        "sha256": sha256(src),
        "size": st.st_size,
        "mtime": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
        "frozen_at": now,
        "note": "frozen before answer-key access",
    })

manifest = {
    "eval": "quantamm-2024-12-eval",
    "frozen_at": now,
    "answer_key_access_status": "freeze_complete_not_yet_accessed",
    "artifact_count": len(entries),
    "missing": missing,
    "artifacts": entries,
}
(SNAP / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))

# flip scope status
sp = ROOT / "scope/program_scope.json"
ps = json.loads(sp.read_text())
ps["answer_key_access_status"] = "freeze_complete_not_yet_accessed"
sp.write_text(json.dumps(ps, indent=2))

print(f"[ok] froze {len(entries)} artifacts → {SNAP}")
if missing:
    print(f"  [warn] {len(missing)} missing (not present): {missing}")
print(f"  MANIFEST: {SNAP/'MANIFEST.json'}")
