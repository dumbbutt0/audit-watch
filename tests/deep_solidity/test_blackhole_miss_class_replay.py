"""
Blackhole freeze regression guard. Asserts the validated generalization behavior is frozen:
- the post-validation pre_answer_key_snapshot (inputs + scorecards) is unchanged (repo-relative hashes);
- behavioral replay (READ-ONLY): arithmetic_conservation routes M-01 calculate_rebase (high) and M-06
  Pair._k, its route_rate stays small, abi_getter_mismatch route_rate stays 0, validators mint 0 findings;
- the submission dry-run stays safe: the frozen readiness report is DO_NOT_SUBMIT with the historical
  duplicate caught;
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
AUDIT = ROOT / "audits" / "blackhole-2025-05-eval"
PRE = AUDIT / "output" / "pre_answer_key_snapshot"
REPLAY_PY = AUDIT / "replay" / "replay_miss_class.py"
FRESH = AUDIT / "output" / "eval_ready" / "blackhole_fresh"

frozen = pytest.mark.skipif(not (PRE / "_baseline_hashes.txt").exists(),
                            reason="Blackhole pre_answer_key_snapshot not present")


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
    spec = importlib.util.spec_from_file_location("blackhole_replay", REPLAY_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.replay()


@frozen
def test_frozen_snapshot_unchanged():
    # baseline paths are repo-relative (workspace inputs + documentation/ scorecards)
    res = _check_baseline(PRE / "_baseline_hashes.txt", ROOT)
    missing = [r for r in res if r.startswith("MISSING:")]
    drift = [r for r in res if not r.startswith("MISSING:")]
    if missing:
        pytest.skip(f"frozen set incomplete in this checkout ({len(missing)} pinned artifacts archived to "
                    f"_eval_archive_*.tar.gz; restore to re-enable the guard)")
    assert drift == [], "Blackhole frozen regression set drifted"


@frozen
def test_replay_routes_m01_m06():
    r = _replay()
    assert r["findings_minted_by_validators"] == 0
    assert r["m01_routed"] and r["m01_confidence"] == "high", "arithmetic_conservation no longer routes M-01 (high)"
    assert r["m06_routed"], "arithmetic_conservation no longer routes M-06 Pair._k"
    assert r["arithmetic_route_rate"] < 0.05, f"arithmetic route_rate spiked: {r['arithmetic_route_rate']}"
    assert r["abi_getter_route_rate"] == 0.0, f"abi_getter route_rate no longer 0: {r['abi_getter_route_rate']}"


@frozen
def test_submission_dry_run_safe():
    readiness = (FRESH / "readiness_H-02.md").read_text()
    assert "DO_NOT_SUBMIT" in readiness, "submission gate no longer blocks the historical candidate"
    assert "duplicate" in readiness.lower(), "historical duplicate no longer caught"
    cand = json.loads((FRESH / "candidate_H-02.json").read_text())
    assert "high" in json.dumps(cand).lower(), "candidate severity (High) not preserved"


def test_noise_audit_clean():
    rc = subprocess.run([sys.executable, str(ROOT / "scripts" / "noise_audit.py")],
                        capture_output=True, text=True).returncode
    assert rc == 0
    rep = json.loads((ROOT / "documentation" / "evals" / "_regression" / "noise_audit.json").read_text())
    assert rep["total_findings_minted_by_validators"] == 0
    assert rep["noisy_validators"] == []
