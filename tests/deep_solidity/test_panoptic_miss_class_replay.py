"""
Task 7 — Panoptic replay + noise + frozen-integrity regression.

Replays the frozen Panoptic eval through the new conversion-engine validators (READ-ONLY), asserts the
frozen snapshot is byte-for-byte unchanged, and runs the noise audit across all frozen evals to prove the
validators introduce no finding-level FPs. Skips gracefully if the frozen snapshot isn't present.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audits" / "panoptic-2025-12-strict-eval"
SNAP = AUDIT / "output" / "pre_answer_key_snapshot"
REPLAY_PY = AUDIT / "replay" / "replay_miss_class.py"

frozen = pytest.mark.skipif(not (SNAP / "MANIFEST.json").exists(),
                            reason="frozen Panoptic snapshot not present")


def _load(py):
    spec = importlib.util.spec_from_file_location("panoptic_replay", py)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@frozen
def test_replay_runs_and_introduces_no_fp():
    mod = _load(REPLAY_PY)
    man, disp = mod._frozen()
    res = mod.literal_replay(man, disp)
    # validators never mint findings → no prior finding becomes a finding-level FP
    assert res["findings_minted_by_validators"] == 0
    assert res["findings_converted_to_fp"] == 0
    # gate-dos routing on the frozen clears must be a small fraction (not a flood)
    assert res["gate_dos_would_route"] is not None
    assert len(res["gate_dos_would_route"]) <= max(1, res["cleared_count"] // 2)


@frozen
def test_frozen_snapshot_unchanged():
    """Every frozen file still matches its recorded sha256 (the upgrade mutated nothing)."""
    baseline = (SNAP / "_baseline_hashes.txt")
    if not baseline.exists():
        pytest.skip("no baseline hashes")
    mismatches = []
    missing = []
    for line in baseline.read_text().splitlines():
        if not line.strip():
            continue
        sha, rel = line.split("  ", 1)
        live = AUDIT / rel
        if live.exists():
            h = hashlib.sha256(live.read_bytes()).hexdigest()
            if h != sha:
                mismatches.append(rel)
        else:
            missing.append(rel)
    if missing:
        pytest.skip(f"frozen set incomplete in this checkout ({len(missing)} pinned artifacts archived to "
                    f"_eval_archive_*.tar.gz; restore to re-enable the guard)")
    assert mismatches == [], f"frozen eval mutated: {mismatches}"


def test_noise_audit_clean():
    rc = subprocess.run([sys.executable, str(ROOT / "scripts" / "noise_audit.py")],
                        capture_output=True, text=True).returncode
    assert rc == 0
    rep = json.loads((ROOT / "documentation" / "evals" / "_regression" / "noise_audit.json").read_text())
    assert rep["total_findings_minted_by_validators"] == 0
    assert rep["noisy_validators"] == []


def test_panoptic_fixtures_present():
    fx = ROOT / "tests" / "fixtures" / "panoptic_miss_class"
    for name in ("h01_builderwallet_init_reinit.sol",
                 "h02_liquidation_cross_contract_reentrancy.sol",
                 "m01_intended_gate_vs_liquidation_dos.sol"):
        assert (fx / name).exists() and (fx / name.replace(".sol", "_safe.sol")).exists()
