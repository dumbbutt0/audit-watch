#!/usr/bin/env python3
"""P188 — tests for the advisory adjudication-support detectors in validate_deep_pass_mechanisms.py.

Covers the six required cases (responsive pass · non-responsive fail · severity-floor fail · valid severity
rejection pass · NEEDS_HARNESS escalation · source-disproven rejection allowed) plus the frozen-P186 replay
acceptance assertions (M-02 non-responsive, M-06 severity-floor, zero stable-selection false positives)."""
import json
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts").is_dir())
sys.path.insert(0, str(ROOT / "scripts"))
import validate_deep_pass_mechanisms as v  # noqa: E402

P186_RAW = ROOT / "documentation/research/assisted_mode/p186_fresh_model_blind_selection/raw_outputs"


# --- unit: detectors ----------------------------------------------------------------------------------------
def _reject(**kw):
    base = {"mechanism": "", "rejecting_source_fact": "", "why_unexploitable": "", "who_loses": "", "who_gains": ""}
    base.update(kw)
    return base


def test_responsive_rejection_passes():
    inv = ["stale accounting via lpTokenDepositValueChange truncation"]
    row = _reject(mechanism="stale accounting via lpTokenDepositValueChange truncation",
                  rejecting_source_fact="lpTokenDepositValueChange is scaled by 1e18 before division; no truncation",
                  who_loses="n/a")
    assert v.detect_non_responsive_rejection(row, inv) is None


def test_non_responsive_rejection_flagged():
    inv = ["stale accounting snapshot (feePerLP precision via lpTokenDepositValueChange)"]
    row = _reject(mechanism="stale accounting snapshot (feePerLP precision)",
                  rejecting_source_fact="feePerLP 1e18 units, feeAmount 1e18 units, mulDown cancels scale",
                  who_loses="withdrawing user dust")
    flag = v.detect_non_responsive_rejection(row, inv)
    assert flag and flag["flag"] == "non_responsive_rejection"
    assert flag["claimed_locus"] == "lpTokenDepositValueChange"


def test_severity_floor_misrejection_flagged():
    row = _reject(mechanism="external-call failure/DoS on _getOracleData",
                  rejecting_source_fact="revert propagates; view function",
                  why_unexploitable="liveness/DoS not fund-loss; no inconsistent state",
                  who_loses="pool operators/LPs (no timely rebalance)")
    flag = v.detect_severity_floor_misrejection(row)
    assert flag and flag["flag"] == "severity_floor_misrejection"
    assert flag["severity_floor"] == "Medium"


def test_valid_severity_rejection_not_flagged():
    """A genuine no-impact rejection (dust / self-funded, no victim) must NOT be flagged — reject-first intact."""
    row = _reject(mechanism="rounding dust on withdrawal",
                  rejecting_source_fact="self-funded dust only, no funds stolen",
                  why_unexploitable="dust, no victim", who_loses="nobody")
    assert v.detect_severity_floor_misrejection(row) is None


def test_source_disproven_rejection_allowed():
    """A rejection disproven by source (no DoS-impact + no high-bar reason) is not flagged by either detector."""
    inv = ["reentrancy via external call before state cleanup"]
    row = _reject(mechanism="reentrancy via external call",
                  rejecting_source_fact="only external calls are view reads; no user callback; no state write",
                  why_unexploitable="no attacker-controlled callback", who_loses="n/a")
    assert v.detect_non_responsive_rejection(row, inv) is None
    assert v.detect_severity_floor_misrejection(row) is None


def test_needs_harness_recognized_and_not_flagged():
    d = {"mechanism_inventory": ["a", "b", "c"],
         "selected_mechanisms": [{"who_loses": "victim"}],
         "unresolved_mechanisms": [{"mechanism": "truncation drift", "status": "NEEDS_HARNESS",
                                    "who_loses": "protocol"}],
         "rejected_mechanisms": [_reject(mechanism="x", rejecting_source_fact="disproven by source")],
         "impact_direction": "attacker gains, victim loses value via fee state; not self-funded/dust/admin/timing",
         "stop_condition": "satisfied"}
    res = v.check_output(d)
    assert res["needs_harness_count"] == 1
    assert "non_responsive_rejection" not in res["flags"]
    assert "severity_floor_misrejection" not in res["flags"]


# --- acceptance: frozen P186 replay ------------------------------------------------------------------------
def _load(name):
    return json.loads((P186_RAW / name).read_text())


def test_frozen_m02_non_responsive():
    res = v.check_output(_load("onAfterRemoveLiquidity.json"))
    assert "non_responsive_rejection" in res["flags"]
    nr = next(f for f in res["flag_details"] if f["flag"] == "non_responsive_rejection")
    assert nr["claimed_locus"] == "lpTokenDepositValueChange"


def test_frozen_m06_severity_floor():
    res = v.check_output(_load("UpdateWeightRunner__getData.json"))
    assert "severity_floor_misrejection" in res["flags"]


def test_frozen_stable_selections_zero_false_positives():
    new_flags = ("non_responsive_rejection", "severity_floor_misrejection")
    for name in ("afterUpdate.json", "onAfterSwap.json", "MultiHopOracle__getData.json"):
        res = v.check_output(_load(name))
        assert not any(f in res["flags"] for f in new_flags), (name, res["flags"])


def test_checker_remains_advisory():
    """main() must always return 0 (never blocks)."""
    import inspect
    src = inspect.getsource(v.main)
    assert "return 0" in src
    assert "sys.exit(1)" not in src and "SystemExit(1)" not in src


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
