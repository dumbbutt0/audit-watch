#!/usr/bin/env python3
"""
freeze_blind.py (NOYA 2024-04 eval — POST-VALIDATION regression freeze) — deliberate freeze cycle.

NOYA's "answer key" was the public Code4rena report from the start; there was no blind phase. So this is a
post-validation regression snapshot — but it uses the `pre_answer_key_snapshot/` dir name so
scripts/noise_audit.py (glob fixed to that name) auto-includes it (NOYA has 0 cleared dispositions →
0% route → noise-safe).

Freezes the deterministic, timestamp-free inputs + scorecards that encode the validated connector/TVL
routing result. The lens audit JSONs (connector_position_accounting / arithmetic_conservation /
abi_getter_mismatch) carry a volatile `generated_at` and are NOT hash-frozen — their routes
(H-11/H-19/H-13/H-12, Aerodrome dedup, abi_getter quiet) are guarded by behavioral replay in the test.

Records sha256 of the LIVE source (repo-relative paths) so the regression test detects real regeneration
drift. Run: python audits/noya-2024-04-eval/logs/freeze_blind.py
"""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]            # audits/noya-2024-04-eval
REPO = Path(__file__).resolve().parents[3]             # repo root (targets repo-relative incl. docs)
SNAP = AUDIT / "output" / "pre_answer_key_snapshot"
SNAP.mkdir(parents=True, exist_ok=True)

# repo-relative, timestamp-free. coverage_manifest/dispositions first so noise_audit's suffix `_find` works.
TARGETS = [
    "audits/noya-2024-04-eval/output/coverage_manifest.json",
    "audits/noya-2024-04-eval/output/coverage_dispositions.json",
    "audits/noya-2024-04-eval/output/eval_ready/noya_fresh/route_scorecard.json",
    "audits/noya-2024-04-eval/output/eval_ready/noya_fresh/candidate_H-08.json",
    "audits/noya-2024-04-eval/output/eval_ready/noya_fresh/readiness_H-08.md",
    "documentation/evals/noya-2024-04/answer_key.md",
    "documentation/evals/noya-2024-04/final_eval_report.md",
    "documentation/evals/noya-2024-04/connector_position_accounting_report.md",
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


now = datetime.now(timezone.utc).isoformat()
entries, missing, baseline = [], [], []
for rel in TARGETS:
    src = REPO / rel
    if not src.exists():
        missing.append(rel); continue
    dest = SNAP / rel.replace("/", "__")
    shutil.copy2(src, dest)
    digest = sha256(src)
    baseline.append(f"{digest}  {rel}")               # hash of LIVE source, repo-relative path
    st = src.stat()
    entries.append({"path": rel, "snapshot_copy": str(dest.relative_to(AUDIT)), "sha256": digest,
                    "size": st.st_size, "frozen_at": now, "note": "validated regression artifact"})

(SNAP / "_baseline_hashes.txt").write_text("\n".join(baseline) + "\n")
(SNAP / "MANIFEST.json").write_text(json.dumps({
    "eval": "noya-2024-04-eval",
    "snapshot": "pre_answer_key_snapshot",
    "frozen_at": now,
    "note": ("POST-VALIDATION regression freeze — NOYA's answer key was the public C4 report; frozen after "
             "validation, not blind. Lens audit JSONs (timestamped) are guarded by behavioral replay, not "
             "byte-hash. Dir name matches the noise_audit glob (0 cleared dispositions → noise-safe). Protects "
             "the tractable connector_position_accounting sub-signals (H-11/H-19/H-13/H-12) + H-08 special_focus; "
             "NOT the deferred semantic-completeness model (H-06 omitted staked balance, H-20 tick ownership)."),
    "answer_key_access_status": "public_from_start_post_validation_freeze",
    "artifact_count": len(entries), "missing": missing, "artifacts": entries,
}, indent=2))

print(f"[ok] froze {len(entries)} regression artifacts → {SNAP}")
if missing:
    print(f"  [warn] missing: {missing}")
print(f"  baseline: {SNAP/'_baseline_hashes.txt'}  ·  MANIFEST: {SNAP/'MANIFEST.json'}")
