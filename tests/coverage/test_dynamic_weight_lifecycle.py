"""
Tests for the P174 dynamic-weight-lifecycle (F1) recall lens (no LLM, no network).

A dynamic-weight lifecycle surface (setWeights/update/onSwap/computeBalance) may NOT be cleared without a
lifecycle-completeness proof (sum/bounds/epsilon/interval/staleness). RE-SURFACE ONLY: a thin clear is routed
to needs_deep_pass (dynamic_weight_lifecycle_review) — never a finding/severity/routing. Mirrors the
math_estimator test: taxonomy FP gate, validate advisory/strict, coverage_sweep_write downgrade-under-full-audit,
and apply_update proof pass-through.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
dwl = importlib.import_module("dynamic_weight_lifecycle_taxonomy")
validator = importlib.import_module("validate_dynamic_weight_lifecycle_clears")
sweep_write = importlib.import_module("coverage_sweep_write")
ucd = importlib.import_module("update_coverage_disposition")

MID = "function:QuantAMMWeightedPool:setWeights#abcd"


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _write(ws, rel, obj):
    p = ws / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))
    return p


def _run(mod, argv=None):
    old = sys.argv
    sys.argv = [mod.__name__] + (argv or [])
    try:
        return mod.main()
    finally:
        sys.argv = old


def _valid_proof(**over):
    p = {"normalized_sum_proof": "require(sum == ONE) at QuantAMMWeightedPool.sol:42",
         "per_weight_bounds_proof": "_clampWeights enforces min/max bound at line 50",
         "epsilon_guard_proof": "_guardQuantAMMWeights epsilon check at line 55",
         "update_interval_proof": "require(block.timestamp >= last + interval) at line 30",
         "staleness_proof": "lastUpdateIntervalTime updated at line 60",
         "permissionless_paths_considered": "performUpdate is the only permissionless path; all checks run there"}
    p.update(over)
    return p


# ---------- taxonomy FP controls ----------
def test_setweights_missing_interval_is_lifecycle_sensitive():
    cls = dwl.classify("setWeights", "function setWeights(uint[] w) external", "P.sol", "QuantAMMWeightedPool",
                       snippet="for (uint i;i<n;){ weights[i] = w[i]; } require(_sum(w)==ONE);")
    assert cls["lifecycle_sensitive"] is True
    assert "update_interval" in cls["missing_lifecycle_checks"]


def test_onswap_view_still_sensitive_unambiguous():
    cls = dwl.classify("onSwap", "function onSwap(PoolSwapParams request) public view", "P.sol",
                       "QuantAMMWeightedPool", snippet="uint w = _getNormalizedWeight(); maxTradeSizeRatio;")
    assert cls["lifecycle_sensitive"] is True  # unambiguous entrypoint survives the getter cut


def test_plain_swap_transfer_getter_not_sensitive():
    assert dwl.classify("swapFrom", "external", "W.sol", "Well", "reserves[i]+=a;")["lifecycle_sensitive"] is False
    assert dwl.classify("transfer", "external", "T.sol", "T", "_bal[to]+=a;")["lifecycle_sensitive"] is False
    assert dwl.classify("balanceOf", "external view", "T.sol", "T", "return x;")["lifecycle_sensitive"] is False


def test_admin_only_nonentrypoint_setter_excluded():
    cls = dwl.classify("setMaxTotalSupply", "function setMaxTotalSupply(uint x) external onlyController",
                       "M.sol", "Market", "maxSupply = x;")
    assert cls["lifecycle_sensitive"] is False  # role-gated + not an unambiguous lifecycle entrypoint


# ---------- proof validation ----------
def test_missing_proof():
    assert validator.validate_proof(None)[0] == "missing_lifecycle_proof"


def test_incomplete_proof():
    assert validator.validate_proof({"normalized_sum_proof": "x"})[0] == "incomplete_lifecycle_proof"


def test_full_concrete_proof_valid():
    assert validator.validate_proof(_valid_proof())[0] == "lifecycle_proof_valid"


def test_boilerplate_proof_is_confirmatory():
    boiler = {k: "enforced" for k in validator.REQUIRED_PROOF_FIELDS}
    assert validator.validate_proof(boiler)[0] == "confirmatory_lifecycle_proof"


# ---------- writer downgrade enforcement (re-surface only) ----------
def _ws_for_sweep(ws):
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        {"id": MID, "kind": "function", "contract": "QuantAMMWeightedPool", "file": "P.sol",
         "name": "setWeights", "signature": "function setWeights(uint[] w) external",
         "in_scope": True, "attack_surface_score": 3, "tags": [],
         "source_span": {"start_line": 1, "end_line": 1}}]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": MID, "status": "unassigned", "evidence": [], "finding_refs": [], "clear_reason": None}]})


def test_writer_routes_proofless_lifecycle_clear_under_full_audit(ws, monkeypatch):
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    _ws_for_sweep(ws)
    # clear-text deliberately free of dependency / estimator tokens so F1 is the routing path under test
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": MID, "disposition": "cleared", "evidence_span": "P.sol:5",
         "reason": "the weight setter writes the new weights array; looks fine",
         "attacker_reachability": "called by the update runner",
         "guard_or_invariant": "weights written from the rule output",
         "no_impact_reason": "weights stay within the configured numeric range"}]})
    assert _run(sweep_write) == 0
    item = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}[MID]
    assert item["status"] == "assigned"               # RE-SURFACE: routed to deep pass
    assert item["assigned_pass"] == "deep"
    assert item["assigned_agent"] == "dynamic_weight_lifecycle_review"
    assert "finding_refs" not in item or not item["finding_refs"]   # never minted a finding
    assert "severity" not in item                                   # never set severity
    # no SWP finding file produced for this routing
    fpath = ws / "output" / "findings_coverage_sweep.json"
    if fpath.exists():
        assert all(MID not in (f.get("manifest_refs") or []) for f in json.loads(fpath.read_text()).get("findings", []))


def test_writer_clears_lifecycle_with_valid_proof_under_full_audit(ws, monkeypatch):
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    _ws_for_sweep(ws)
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": MID, "disposition": "cleared", "evidence_span": "P.sol:5",
         # clear-text deliberately free of dependency tokens (guard/invariant/lifecycle/clamp/…) so the
         # dependency block does not route first; this isolates the F1 proof-acceptance path.
         "reason": "the setter writes the new weight array from the caller arguments; math re-derived by hand",
         "attacker_reachability": "called by the update runner",
         "guard_or_invariant": "weights taken directly from the function input array",
         "no_impact_reason": "output stays within the configured numeric range",
         "dynamic_weight_lifecycle_proof": _valid_proof()}]})
    assert _run(sweep_write) == 0
    item = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}[MID]
    assert item["status"] == "cleared"
    assert item.get("dynamic_weight_lifecycle_proof", {}).get("normalized_sum_proof")  # proof preserved


def test_writer_does_not_route_when_lifecycle_strict_off(ws, monkeypatch):
    monkeypatch.delenv("AUDITWATCH_FULL_AUDIT", raising=False)
    _ws_for_sweep(ws)
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": MID, "disposition": "cleared", "evidence_span": "P.sol:5",
         "reason": "weight setter reviewed; writes new weights",
         "attacker_reachability": "update runner", "guard_or_invariant": "rule output",
         "no_impact_reason": "within range"}]})
    assert _run(sweep_write) == 0
    item = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}[MID]
    assert item["status"] == "cleared"  # advisory when not full-audit strict


def test_apply_update_preserves_lifecycle_proof():
    d = {"manifest_id": "x", "evidence": [], "finding_refs": []}
    errs = ucd.apply_update(d, "cleared", evidence=["P.sol:1"], clear_reason="reviewed",
                            dynamic_weight_lifecycle_proof=_valid_proof())
    assert errs == []
    assert d["dynamic_weight_lifecycle_proof"]["staleness_proof"]
