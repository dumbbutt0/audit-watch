#!/usr/bin/env python3
"""
freeze_blind.py (Blackhole eval — POST-VALIDATION regression freeze) — deliberate freeze cycle.

Blackhole's "answer key" was the public Code4rena report from the start; there was no blind phase. So this
is a post-validation regression snapshot, NOT a blind one — but it uses the `pre_answer_key_snapshot/` dir
name so scripts/noise_audit.py (whose glob is fixed to that name) auto-includes it (Blackhole has 0 cleared
dispositions → 0% route → noise-safe).

Freezes the deterministic, timestamp-free inputs + scorecards that encode the validated routing /
reward-conversion / generalization result. The lens audit JSONs (arithmetic_conservation_audit.json /
abi_getter_mismatch_audit.json) carry a volatile `generated_at` and are NOT hash-frozen — their routes
(M-01 calculate_rebase, M-06 _k, abi_getter route_rate 0) are guarded by behavioral replay in the test.

Records sha256 of the LIVE source (repo-relative paths) so the regression test detects real regeneration
drift. Run: python audits/blackhole-2025-05-eval/logs/freeze_blind.py
"""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]            # audits/blackhole-2025-05-eval
REPO = Path(__file__).resolve().parents[3]             # repo root (targets are repo-relative incl. docs)
SNAP = AUDIT / "output" / "pre_answer_key_snapshot"
SNAP.mkdir(parents=True, exist_ok=True)

# repo-relative, timestamp-free. coverage_manifest/dispositions first so noise_audit's suffix `_find` works.
TARGETS = [
    "audits/blackhole-2025-05-eval/output/coverage_manifest.json",
    "audits/blackhole-2025-05-eval/output/coverage_dispositions.json",
    "audits/blackhole-2025-05-eval/output/eval_ready/blackhole_fresh/route_scorecard.json",
    "audits/blackhole-2025-05-eval/output/eval_ready/blackhole_fresh/candidate_H-02.json",
    "audits/blackhole-2025-05-eval/output/eval_ready/blackhole_fresh/readiness_H-02.md",
    "documentation/evals/blackhole-2025-05/answer_key.md",
    "documentation/evals/blackhole-2025-05/final_eval_report.md",
    "documentation/evals/blackhole-2025-05/deep_pass_scorecard.md",
    "documentation/evals/blackhole-2025-05/arithmetic_conservation_report.md",
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
    "eval": "blackhole-2025-05-eval",
    "snapshot": "pre_answer_key_snapshot",
    "frozen_at": now,
    "note": ("POST-VALIDATION regression freeze — Blackhole's answer key was the public C4 report; frozen "
             "after validation, not blind. Lens audit JSONs (timestamped) are guarded by behavioral replay, "
             "not byte-hash. Dir name matches the noise_audit glob (0 cleared dispositions → noise-safe)."),
    "answer_key_access_status": "public_from_start_post_validation_freeze",
    "artifact_count": len(entries), "missing": missing, "artifacts": entries,
}, indent=2))

print(f"[ok] froze {len(entries)} regression artifacts → {SNAP}")
if missing:
    print(f"  [warn] missing: {missing}")
print(f"  baseline: {SNAP/'_baseline_hashes.txt'}  ·  MANIFEST: {SNAP/'MANIFEST.json'}")
