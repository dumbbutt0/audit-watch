"""
Ethos Reserve 2023-02 (Liquity-fork CDP) freeze regression guard for the PROMOTED
liquidation_health_accounting behavior (advisory, high-only, strict full-audit) + internal-helper volume
control. Asserts:
- the post-validation pre_answer_key_snapshot (inputs + scorecards) is unchanged (repo-relative hashes);
- behavioral replay (READ-ONLY): H-01 StabilityPool offset/updateRewardSum route, M-09 redeemCollateral routes,
  M-10 liquidate/liquidateTroves/batchLiquidateTroves route (context/PARTIAL hosts), helper volume control
  works (context_helpers attached on redeemCollateral/offset; attached helpers are NOT independently routed;
  orphan _liquidate* route standalone), routed < raw (volume reduced), routing is high-only, 0 wrong-domain FP,
  and an isolated gate run routes every high id to needs_deep_pass (never a finding) carrying context_helpers;
- noise_audit is clean across all frozen snapshots.
No production logic is exercised for mutation — the lens is read-only on dispositions and the gate check runs
in a throwaway workspace.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audits" / "ethos-reserve-2023-02-liquidation-health"
PRE = AUDIT / "output" / "pre_answer_key_snapshot"
REPLAY_PY = AUDIT / "replay" / "replay_lha.py"

frozen = pytest.mark.skipif(not (PRE / "_baseline_hashes.txt").exists(),
                            reason="Ethos pre_answer_key_snapshot not present")


def _check_baseline(baseline: Path, base_dir: Path) -> list[str]:
    out = []
    for line in baseline.read_text().splitlines():
        if not line.strip():
            continue
        sha, rel = line.split("  ", 1)
        live = base_dir / rel
        if not live.exists():
            out.append(f"MISSING:{rel}")
        elif hashlib.sha256(live.read_bytes()).hexdigest() != sha:
            out.append(rel)
    return out


def _replay():
    spec = importlib.util.spec_from_file_location("ethos_lha_replay", REPLAY_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.replay()


@frozen
def test_frozen_snapshot_unchanged():
    res = _check_baseline(PRE / "_baseline_hashes.txt", ROOT)
    missing = [r for r in res if r.startswith("MISSING:")]
    drift = [r for r in res if not r.startswith("MISSING:")]
    if missing:
        pytest.skip(f"frozen set incomplete in this checkout ({len(missing)} pinned artifacts archived to "
                    f"_eval_archive_*.tar.gz; restore to re-enable the guard)")
    assert drift == [], "Ethos frozen regression set drifted"


@frozen
def test_replay_routes_promoted_findings():
    r = _replay()
    assert r["h01_offset"] and r["h01_update_reward_sum"], "H-01 StabilityPool offset/updateRewardSum regressed"
    assert r["m09_redeem_collateral"], "M-09 RedemptionHelper.redeemCollateral route regressed"
    # M-10 liquidation family routes (context/PARTIAL hosts)
    assert r["m10_liquidate"] and r["m10_liquidate_troves"] and r["m10_batch_liquidate_troves"], \
        "M-10 liquidate family no longer routes"
    # high-only + 0 wrong-domain
    assert r["routed_high_only"], "a non-high candidate routed (routing must be high-only)"
    assert r["wrong_domain_contracts"] == [], f"wrong-domain FP present: {r['wrong_domain_contracts']}"


@frozen
def test_replay_helper_volume_control():
    r = _replay()
    # same-contract helpers a routed entrypoint calls are attached as context...
    assert r["redeem_helper_attached"], "_redeemCollateralFromTrove no longer attached to redeemCollateral"
    assert r["offset_helpers_attached"], "_computeRewardsPerUnitStaked no longer attached to offset"
    # ...and are NOT independently routed; orphans route standalone → routed < raw (volume reduced)
    assert r["attached_not_routed"], "an attached helper leaked into the routed set"
    assert r["routed_lt_raw"], "routed set is not smaller than the raw helper-heavy candidate set"
    assert r["routed_count"] <= 12, f"routed count spiked: {r['routed_count']}"
    assert r["raw_candidates"] <= 24, f"candidate count spiked: {r['raw_candidates']}"


@frozen
def test_replay_gate_routes_needs_deep_pass_not_finding():
    r = _replay()
    assert r["findings_minted_by_validators"] == 0
    assert r["gate_all_needs_deep_pass"], "a routed id did not become needs_deep_pass via the gate"
    assert r["gate_minted_finding"] is False, "the gate minted a finding (must only route to deep pass)"
    assert r["gate_context_helpers_carried"], "context_helpers provenance not carried onto a routed entrypoint"
    assert r["gate_routed"] == r["routed_count"], "not every routed id reached the deep-pass queue"


def test_noise_audit_clean():
    rc = subprocess.run([sys.executable, str(ROOT / "scripts" / "noise_audit.py")],
                        capture_output=True, text=True).returncode
    assert rc == 0
    rep = json.loads((ROOT / "documentation" / "evals" / "_regression" / "noise_audit.json").read_text())
    assert rep["total_findings_minted_by_validators"] == 0
    assert rep["noisy_validators"] == []
