#!/usr/bin/env python3
"""
freeze_blind.py (Hybra eval — LENS REGRESSION freeze) — deliberate freeze cycle.

This does NOT touch the existing blind `output/pre_answer_key_snapshot/` (35 baseline lines — must stay
35/35). The P1/P2/P3 reward arc + abi_getter_mismatch + arithmetic_conservation lenses were validated
POST answer-key, so their result artifacts are frozen separately here, into
`output/lens_regression_snapshot/`. Deterministic; copies the TARGETS and records sha256 of the LIVE source
(so the regression test detects real regeneration drift, not just edits to the copy).

Run: python audits/hybra-finance-2025-10-strict-eval/logs/freeze_blind.py
"""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # the audit workspace dir (independent of active audit)
SNAP = ROOT / "output" / "lens_regression_snapshot"
SNAP.mkdir(parents=True, exist_ok=True)

# Timestamp-free result artifacts that encode the validated reward/P-series behavior. (The lens audit JSONs
# abi_getter_mismatch_audit.json / arithmetic_conservation_audit.json carry a volatile `generated_at` and
# are deliberately NOT hash-frozen — their routes are guarded by behavioral replay in the regression test.)
TARGETS = [
    "output/eval_ready/p1p2_fresh/scorecard_p1p2.json",
    "output/eval_ready/p1p2_fresh/p3_loop_reduction.json",
    "output/eval_ready/p1p2_fresh/validator_before.json",
    "output/eval_ready/p1p2_fresh/validator_after.json",
    "output/eval_ready/p1p2_fresh/fresh_dispositions_6fn.json",
    "output/eval_ready/reward_route_classification.json",
    "output/eval_ready/scorecard_primary.json",
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


now = datetime.now(timezone.utc).isoformat()
entries, missing, baseline = [], [], []
for rel in TARGETS:
    src = ROOT / rel
    if not src.exists():
        missing.append(rel); continue
    dest = SNAP / rel.replace("/", "__")
    shutil.copy2(src, dest)
    digest = sha256(src)
    baseline.append(f"{digest}  {rel}")          # hash of the LIVE source, live path → real drift detection
    st = src.stat()
    entries.append({"path": rel, "snapshot_copy": str(dest.relative_to(ROOT)), "sha256": digest,
                    "size": st.st_size, "frozen_at": now,
                    "note": "validated post-answer-key lens/P-series result — regression-frozen"})

(SNAP / "_baseline_hashes.txt").write_text("\n".join(baseline) + "\n")
(SNAP / "MANIFEST.json").write_text(json.dumps({
    "eval": "hybra-finance-2025-10-strict-eval",
    "snapshot": "lens_regression_snapshot",
    "frozen_at": now,
    "note": ("POST-answer-key validated freeze of the reward P1/P2/P3 result artifacts. Separate from the "
             "blind pre_answer_key_snapshot (35/35, untouched). abi_getter_mismatch (M-07) and "
             "arithmetic_conservation routes are guarded by behavioral replay, not byte-hash."),
    "artifact_count": len(entries), "missing": missing, "artifacts": entries,
}, indent=2))

print(f"[ok] froze {len(entries)} lens/P-series result artifacts → {SNAP}")
if missing:
    print(f"  [warn] missing: {missing}")
print(f"  baseline: {SNAP/'_baseline_hashes.txt'}  ·  MANIFEST: {SNAP/'MANIFEST.json'}")
