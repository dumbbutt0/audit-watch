"""
Task 7/8 — Revert Lend replay + fixtures + noise regression. Replays the frozen Revert Lend eval through the
new spec-checklist + waiver-risk validators (READ-ONLY), asserts the frozen snapshot is unchanged, and runs
the noise audit across all frozen evals (validators never mint findings → no finding-level FP).
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audits" / "revert-lend-2024-03-strict-eval"
SNAP = AUDIT / "output" / "pre_answer_key_snapshot"
REPLAY_PY = AUDIT / "replay" / "replay_miss_class.py"

frozen = pytest.mark.skipif(not (SNAP / "MANIFEST.json").exists(),
                            reason="frozen Revert Lend snapshot not present")


def _load(py):
    spec = importlib.util.spec_from_file_location("revert_replay", py)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@frozen
def test_replay_routes_spec_clears_no_fp():
    mod = _load(REPLAY_PY)
    res = mod.replay()
    assert res["findings_minted_by_validators"] == 0
    # the frozen clears predate the checklists, so some spec-heavy clears would now route (recall-positive)
    assert isinstance(res["spec_checklist_would_route"], list)
    assert isinstance(res["high_risk_items_under_cluster_waivers"], list)


@frozen
def test_frozen_snapshot_unchanged():
    baseline = SNAP / "_baseline_hashes.txt"
    if not baseline.exists():
        pytest.skip("no baseline hashes")
    mismatches = []
    for line in baseline.read_text().splitlines():
        if not line.strip():
            continue
        sha, rel = line.split("  ", 1)
        live = AUDIT / rel
        if live.exists():
            if hashlib.sha256(live.read_bytes()).hexdigest() != sha:
                mismatches.append(rel)
    assert mismatches == [], f"frozen eval mutated: {mismatches}"


def test_noise_audit_clean():
    rc = subprocess.run([sys.executable, str(ROOT / "scripts" / "noise_audit.py")],
                        capture_output=True, text=True).returncode
    assert rc == 0
    rep = json.loads((ROOT / "documentation" / "evals" / "_regression" / "noise_audit.json").read_text())
    assert rep["total_findings_minted_by_validators"] == 0
    assert rep["noisy_validators"] == []


def test_fixtures_present():
    fx = ROOT / "tests" / "fixtures" / "revert_lend_miss_class"
    for stem in ("h01_permit_token_substitution", "h02_onreceived_collateral_reentrancy",
                 "h04_transformer_caller_validation", "h05_negative_tick_rounding",
                 "h06_callback_liquidation_prevention", "m04_once_per_block_interest",
                 "m14_erc4626_false_compliance"):
        assert (fx / f"{stem}.sol").exists() and (fx / f"{stem}_safe.sol").exists()
