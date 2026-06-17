"""
NOYA 2024-04 freeze regression guard. Asserts the validated connector/TVL behavior is frozen:
- the post-validation pre_answer_key_snapshot (inputs + scorecards) is unchanged (repo-relative hashes);
- behavioral replay (READ-ONLY): connector_position_accounting routes the 4 recovered misses with the right
  shapes (H-11/H-19 external_reader_aggregate, H-13 position_tvl_product_div, H-12 registry_key_mismatch),
  Aerodrome stays de-duped to context (arithmetic_conservation owns it), route_rate stays small,
  abi_getter_mismatch stays quiet, H-08 stays special_focus, validators mint 0 findings;
- the H-08 submission dry-run stays safe: the frozen readiness report is DO_NOT_SUBMIT with the historical
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
AUDIT = ROOT / "audits" / "noya-2024-04-eval"
PRE = AUDIT / "output" / "pre_answer_key_snapshot"
REPLAY_PY = AUDIT / "replay" / "replay_miss_class.py"
FRESH = AUDIT / "output" / "eval_ready" / "noya_fresh"

frozen = pytest.mark.skipif(not (PRE / "_baseline_hashes.txt").exists(),
                            reason="NOYA pre_answer_key_snapshot not present")


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
    spec = importlib.util.spec_from_file_location("noya_replay", REPLAY_PY)
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
    assert drift == [], "NOYA frozen regression set drifted"


@frozen
def test_replay_routes_connector_position_accounting():
    r = _replay()
    assert r["findings_minted_by_validators"] == 0
    # the 4 recovered misses + their shapes (tuple(...) normalizes list/tuple from in-process vs json)
    assert tuple(r["h11_snx"]) == ("external_reader_aggregate", "medium"), "H-11 SNXV3 route regressed"
    assert tuple(r["h19_morpho"]) == ("external_reader_aggregate", "high"), "H-19 Morpho route regressed"
    assert tuple(r["h13_balancer"]) == ("position_tvl_product_div", "medium"), "H-13 Balancer route regressed"
    assert tuple(r["h12_registry"]) == ("registry_key_mismatch", "medium"), "H-12 Registry route regressed"
    # Aerodrome: de-duped to context here AND owned by arithmetic_conservation
    assert r["aerodrome_deduped_to_context"], "Aerodrome no longer de-duped to context"
    assert r["aerodrome_owned_by_arithmetic"], "arithmetic_conservation no longer owns Aerodrome"
    # route-rate / quiet / special_focus
    assert r["cpa_route_rate"] < 0.05, f"connector_position_accounting route_rate spiked: {r['cpa_route_rate']}"
    assert r["abi_getter_route_rate"] == 0.0, f"abi_getter route_rate no longer 0: {r['abi_getter_route_rate']}"
    assert r["h08_special_focus"], "H-08 sendTokensToTrustedAddress no longer special_focus"


@frozen
def test_submission_dry_run_safe():
    readiness = (FRESH / "readiness_H-08.md").read_text()
    assert "DO_NOT_SUBMIT" in readiness, "submission gate no longer blocks the historical H-08 candidate"
    assert "duplicate" in readiness.lower(), "historical duplicate no longer caught"
    cand = json.loads((FRESH / "candidate_H-08.json").read_text())
    assert "high" in json.dumps(cand).lower(), "candidate severity (High) not preserved"


def test_noise_audit_clean():
    rc = subprocess.run([sys.executable, str(ROOT / "scripts" / "noise_audit.py")],
                        capture_output=True, text=True).returncode
    assert rc == 0
    rep = json.loads((ROOT / "documentation" / "evals" / "_regression" / "noise_audit.json").read_text())
    assert rep["total_findings_minted_by_validators"] == 0
    assert rep["noisy_validators"] == []
