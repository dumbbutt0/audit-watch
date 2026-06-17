#!/usr/bin/env python3
"""
freeze_promotion.py (Ethos Reserve 2023-02, Liquity-fork CDP — POST-VALIDATION regression freeze) —
deliberate freeze cycle for the PROMOTED liquidation_health_accounting behavior (advisory, high-only, strict
full-audit) + the internal-helper volume control.

Ethos's answer key was the public Code4rena report; no blind phase. Post-validation regression snapshot under
the `pre_answer_key_snapshot/` dir name so scripts/noise_audit.py (glob fixed to that name) auto-includes it
(Ethos has 0 cleared dispositions → 0% route → noise-safe).

Freezes the deterministic, timestamp-free inputs + scorecards that encode the validated Ethos routing result.
The lens audit JSON (liquidation_health_accounting_audit.json) carries a volatile `generated_at` and is NOT
hash-frozen — its routes (H-01 offset/updateRewardSum, M-09 redeemCollateral, M-10 liquidate family; helper
volume control; 0 wrong-domain; needs_deep_pass not finding) are guarded by behavioral replay in
replay/replay_lha.py + tests/deep_solidity/test_ethos_lha_promotion_replay.py.

Records sha256 of the LIVE source (repo-relative paths) so the regression test detects real regeneration drift.
Run: python audits/ethos-reserve-2023-02-liquidation-health/logs/freeze_promotion.py
"""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]            # audits/ethos-reserve-2023-02-liquidation-health
REPO = Path(__file__).resolve().parents[3]             # repo root (targets repo-relative incl. docs)
SNAP = AUDIT / "output" / "pre_answer_key_snapshot"
SNAP.mkdir(parents=True, exist_ok=True)

# repo-relative, timestamp-free. coverage_manifest/dispositions first so noise_audit's suffix `_find` works.
TARGETS = [
    "audits/ethos-reserve-2023-02-liquidation-health/output/coverage_manifest.json",
    "audits/ethos-reserve-2023-02-liquidation-health/output/coverage_dispositions.json",
    "documentation/evals/ethos-reserve-2023-02/answer_key.md",
    "documentation/evals/ethos-reserve-2023-02/liquidation_health_validation_report.md",
    "documentation/evals/ethos-reserve-2023-02/liquidation_health_patch_retest.md",
    "documentation/evals/ethos-reserve-2023-02/liquidation_health_promotion.md",
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
    "eval": "ethos-reserve-2023-02-liquidation-health",
    "snapshot": "pre_answer_key_snapshot",
    "frozen_at": now,
    "note": ("POST-VALIDATION regression freeze of the PROMOTED liquidation_health_accounting behavior "
             "(advisory, high-only, strict full-audit) + internal-helper volume control on a Liquity-fork CDP. "
             "Ethos's answer key was the public C4 report; frozen after validation, not blind. The lens audit "
             "JSON (timestamped) is guarded by behavioral replay, not byte-hash. Dir name matches the "
             "noise_audit glob (0 cleared dispositions → noise-safe). Protects H-01 (StabilityPool offset/"
             "updateRewardSum), M-09 (RedemptionHelper.redeemCollateral), M-10 (TroveManager liquidate family), "
             "the helper volume control (context_helpers attached; orphans route standalone), high-only "
             "routing, 0 wrong-domain FP, needs_deep_pass (not finding); NOT the deferred redemption-arbitrage "
             "/ strategy-DoS / borrow-fee families."),
    "answer_key_access_status": "public_from_start_post_validation_freeze",
    "artifact_count": len(entries), "missing": missing, "artifacts": entries,
}, indent=2))

print(f"[ok] froze {len(entries)} regression artifacts → {SNAP}")
if missing:
    print(f"  [warn] missing: {missing}")
print(f"  baseline: {SNAP/'_baseline_hashes.txt'}  ·  MANIFEST: {SNAP/'MANIFEST.json'}")
