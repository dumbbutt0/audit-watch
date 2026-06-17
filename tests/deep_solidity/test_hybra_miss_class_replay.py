"""
Hybra freeze regression guard. Asserts the validated reward arc behavior is frozen:
- the blind pre_answer_key_snapshot stays 35/35, 0 drift (untouched by this freeze cycle);
- the post-answer-key lens_regression_snapshot (P1/P2/P3 result artifacts) is unchanged;
- behavioral replay (READ-ONLY): abi_getter_mismatch routes M-07, arithmetic_conservation route_rate stays
  small, P3 reduced reward prose loops 6→0, P1 still rejects boilerplate, validators mint 0 findings;
- noise_audit is clean across all frozen snapshots.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audits" / "hybra-finance-2025-10-strict-eval"
PRE = AUDIT / "output" / "pre_answer_key_snapshot"
LENS = AUDIT / "output" / "lens_regression_snapshot"
REPLAY_PY = AUDIT / "replay" / "replay_miss_class.py"

frozen = pytest.mark.skipif(not (LENS / "_baseline_hashes.txt").exists(),
                            reason="Hybra lens_regression_snapshot not present")


def _check_baseline(baseline: Path, base_dir: Path) -> list[str]:
    """Re-hash each baseline entry's path under base_dir; return mismatches/missing."""
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
    spec = importlib.util.spec_from_file_location("hybra_replay", REPLAY_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.replay()


def test_pre_answer_key_snapshot_35_unchanged():
    base = PRE / "_baseline_hashes.txt"
    if not base.exists():
        pytest.skip("blind snapshot baseline not present")
    lines = [l for l in base.read_text().splitlines() if l.strip()]
    assert len(lines) == 35, f"blind baseline must stay 35 lines, got {len(lines)}"
    assert _check_baseline(base, AUDIT) == [], "blind pre_answer_key_snapshot drifted"


@frozen
def test_lens_regression_snapshot_unchanged():
    assert _check_baseline(LENS / "_baseline_hashes.txt", AUDIT) == [], "lens_regression artifacts drifted"


@frozen
def test_replay_routes_and_p_series():
    r = _replay()
    assert r["findings_minted_by_validators"] == 0
    assert r["m07_routed"] is True, "abi_getter_mismatch no longer routes Hybra M-07"
    assert r["arithmetic_route_rate"] < 0.05, f"arithmetic_conservation route_rate spiked: {r['arithmetic_route_rate']}"
    assert r["reward_loops_baseline"] == 6 and r["reward_loops_after_p3"] == 0, "P3 reward-loop 6→0 regressed"
    assert r["p1_still_rejects_prose"], "P1 no longer rejects boilerplate reward clears"


def test_noise_audit_clean():
    rc = subprocess.run([sys.executable, str(ROOT / "scripts" / "noise_audit.py")],
                        capture_output=True, text=True).returncode
    assert rc == 0
    rep = json.loads((ROOT / "documentation" / "evals" / "_regression" / "noise_audit.json").read_text())
    assert rep["total_findings_minted_by_validators"] == 0
    assert rep["noisy_validators"] == []
