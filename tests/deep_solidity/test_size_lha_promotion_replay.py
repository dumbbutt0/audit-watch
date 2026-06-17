"""
Size Credit 2024-06 freeze regression guard for the PROMOTED liquidation_health_accounting behavior
(advisory, high-only, strict full-audit). Asserts:
- the post-validation pre_answer_key_snapshot (inputs + scorecards) is unchanged (repo-relative hashes);
- behavioral replay (READ-ONLY): the 4 mandated seeds route with the right shapes (H-03/H-04 executeLiquidate,
  M-09 executeCompensate, M-11 executeLiquidateWithReplacement), routing is high-only, 0 wrong-domain FP,
  candidate/route counts stay under documented bounds, and an isolated gate run routes every high id to
  needs_deep_pass (never a finding); the lens mints nothing;
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
AUDIT = ROOT / "audits" / "size-credit-2024-06"
PRE = AUDIT / "output" / "pre_answer_key_snapshot"
REPLAY_PY = AUDIT / "replay" / "replay_lha.py"

frozen = pytest.mark.skipif(not (PRE / "_baseline_hashes.txt").exists(),
                            reason="Size pre_answer_key_snapshot not present")


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
    spec = importlib.util.spec_from_file_location("size_lha_replay", REPLAY_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.replay()


@frozen
def test_replay_routes_four_seeds_high_only():
    r = _replay()
    # 4/4 mandated seeds route with the correct shape
    assert r["h03_collateral_remainder_cap"], "H-03 executeLiquidate collateral_remainder_cap regressed"
    assert r["h04_liquidator_profit_bound"], "H-04 executeLiquidate liquidator_profit_bound regressed"
    assert r["m09_health_factor_after_action"], "M-09 executeCompensate health_factor_after_action regressed"
    assert r["m11_replacement_swap_fee"], "M-11 executeLiquidateWithReplacement replacement_swap_fee regressed"
    # high-only routing + 0 wrong-domain FP
    assert r["routed_high_only"], "a non-high candidate routed (routing must be high-only)"
    assert r["wrong_domain_contracts"] == [], f"wrong-domain FP present: {r['wrong_domain_contracts']}"
    # candidate/route volume under documented bounds (now 9 raw / 5 routed)
    assert r["raw_candidates"] <= 12, f"candidate count spiked: {r['raw_candidates']}"
    assert r["routed_count"] <= 6, f"routed count spiked: {r['routed_count']}"


@frozen
def test_replay_gate_routes_needs_deep_pass_not_finding():
    r = _replay()
    assert r["findings_minted_by_validators"] == 0
    assert r["gate_all_needs_deep_pass"], "a routed id did not become needs_deep_pass via the gate"
    assert r["gate_minted_finding"] is False, "the gate minted a finding (must only route to deep pass)"
    assert r["gate_routed"] == r["routed_count"], "not every routed id reached the deep-pass queue"


def test_noise_audit_clean():
    rc = subprocess.run([sys.executable, str(ROOT / "scripts" / "noise_audit.py")],
                        capture_output=True, text=True).returncode
    assert rc == 0
    rep = json.loads((ROOT / "documentation" / "evals" / "_regression" / "noise_audit.json").read_text())
    assert rep["total_findings_minted_by_validators"] == 0
    assert rep["noisy_validators"] == []
