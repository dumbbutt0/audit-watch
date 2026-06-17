"""
Tests for the math/estimator proof policy (no LLM, no network).

A math-estimator / guard / formula surface may NOT be strong-cleared on NatSpec/code agreement — its
clear must carry a math_estimator_proof with an independent formula re-derivation (QuantAMM H-11). These
tests cover the taxonomy FP gate, the validate_math_estimator_clears advisory/strict modes, the
coverage_sweep_write downgrade-under-full-audit enforcement, and the apply_update proof pass-through.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
me = importlib.import_module("math_estimator_taxonomy")
validator = importlib.import_module("validate_math_estimator_clears")
sweep_write = importlib.import_module("coverage_sweep_write")
ucd = importlib.import_module("update_coverage_disposition")


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


def _run(mod, argv):
    old = sys.argv
    sys.argv = [mod.__name__] + argv
    try:
        return mod.main()
    finally:
        sys.argv = old


def _full_proof(**over):
    # A genuinely ADVERSARIAL proof: external source, intended != implemented, explicit diff, economic
    # direction naming an economic variable, attacker-favorable boundary search, and impact-if-wrong.
    p = {"math_domain": "covariance", "intended_formula": "A=lambda*A_prev+(1-lambda)*(p-m1)(p-m2)'",
         "implemented_formula": "A=lambda*A_prev + outer(delta1,delta2)*(1-lambda) then div 1e18",
         "formula_source": ["whitepaper", "derived_in_review"],
         "independent_rederivation": "expanded the recurrence from the whitepaper; confirmed (1-lambda) "
                                     "placement and outer-product scaling against the model",
         "input_domain": "lambda in (0,1), prices 18dp", "output_domain": "n x n matrix",
         "scaling_precision": "div by 1e18 after mul", "rounding_behavior": "trunc toward zero",
         "signedness_assumptions": "signed int256, can be negative", "bounds_and_guards": "none required",
         "edge_cases_checked": ["n=1", "zero deltas"], "invariant_preserved": "symmetric PSD-ish",
         "evidence_span": "Cov.sol:47-127",
         "formula_diff": "no operational divergence; (1-lambda) factor and outer product match the model",
         "assumptions": ["lambda set at pool creation and immutable", "prices already normalized to 18dp"],
         "monotonicity_and_economic_direction": "covariance magnitude rises with price deviation; matches "
                                                "the model's expected direction",
         "attacker_favorable_search": "tried n=1, zero deltas, extreme price 2**128, max-lambda boundary; "
                                      "no overflow or sign flip",
         "economic_impact_if_wrong": "a mis-estimated covariance mis-prices rebalancing weights"}
    p.update(over)
    return p


def _manifest_item(name, contract, snippet, file="R.sol", score=3):
    return {"id": f"function:{contract}:{name}#abcd", "kind": "function", "contract": contract,
            "file": file, "name": name, "signature": f"function {name}() internal", "in_scope": True,
            "attack_surface_score": score, "tags": [], "source_span": {"start_line": 1, "end_line": 1}}


# ---------- taxonomy FP controls ----------

def test_covariance_is_math_sensitive():
    cls = me.classify("_calculateQuantAMMCovariance", "", "Cov.sol", "QuantAMMCovarianceBasedRule",
                      snippet="for (uint i;i<n;){ A[i][j] = lambda.mul(prev).div(1e18); }")
    assert cls["math_estimator_sensitive"] is True
    assert cls["math_domain"] == "covariance"
    assert me.is_high_risk(cls) is True


def test_gradient_vector_math_is_sensitive():
    cls = me.classify("_calculateQuantAMMGradient", "", "G.sol", "QuantAMMGradientBasedRule",
                      snippet="for(uint i;i<n;){ state[i]=lambda.mul(prev).div(oneMinusLambda); }")
    assert cls["math_estimator_sensitive"] is True
    assert cls["math_domain"] == "gradient"


def test_simple_arithmetic_helper_not_high_risk():
    cls = me.classify("addFee", "function addFee(uint a, uint b)", "X.sol", "X", snippet="return a + b;")
    assert cls["math_estimator_sensitive"] is False
    assert me.is_high_risk(cls) is False


def test_plain_getter_and_transfer_not_sensitive():
    assert me.classify("getOwner", "", "X.sol", "X", snippet="return owner;")["math_estimator_sensitive"] is False
    assert me.classify("send", "", "X.sol", "X", snippet="token.transfer(to, amount);")["math_estimator_sensitive"] is False


# ---------- proof validation ----------

def test_missing_proof_status():
    assert validator.validate_proof(None)[0] == "missing_math_proof"


def test_natspec_only_proof_fails():
    p = _full_proof(formula_source=["NatSpec", "code"])
    assert validator.validate_proof(p)[0] == "natspec_only_proof"


def test_full_independent_proof_valid():
    assert validator.validate_proof(_full_proof())[0] == "math_proof_valid"


def test_incomplete_proof_fails():
    p = _full_proof(edge_cases_checked=[])
    assert validator.validate_proof(p)[0] == "incomplete_math_proof"


# ---------- validator advisory vs strict ----------

def _ws_with_covariance_clear(ws, proof=None):
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        _manifest_item("_calculateQuantAMMCovariance", "QuantAMMCovarianceBasedRule",
                       "for(uint i;i<n;){A[i][j]=lambda.mul(p).div(1e18);}"),
    ]})
    disp = {"manifest_id": "function:QuantAMMCovarianceBasedRule:_calculateQuantAMMCovariance#abcd",
            "status": "cleared", "evidence": ["Cov.sol:47"], "finding_refs": [],
            "clear_reason": "estimator math reviewed; formulas match NatSpec"}
    if proof:
        disp["math_estimator_proof"] = proof
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [disp]})


def test_validator_advisory_reports_missing_but_exits_zero(ws):
    _ws_with_covariance_clear(ws)  # the H-11 shape: cleared "formulas match NatSpec", no proof
    rc = _run(validator, ["--mode", "advisory"])
    assert rc == 0
    out = json.loads((ws / "output" / "math_estimator_clear_validation.json").read_text())
    assert out["blocking"] == 1
    assert out["by_status"].get("missing_math_proof") == 1


def test_validator_strict_blocks_missing_proof(ws):
    _ws_with_covariance_clear(ws)
    assert _run(validator, ["--mode", "strict"]) == 1


def test_validator_strict_blocks_natspec_only_proof(ws):
    _ws_with_covariance_clear(ws, proof=_full_proof(formula_source=["NatSpec", "code"]))
    assert _run(validator, ["--mode", "strict"]) == 1
    out = json.loads((ws / "output" / "math_estimator_clear_validation.json").read_text())
    assert out["by_status"].get("natspec_only_proof") == 1


def test_validator_passes_with_independent_proof(ws):
    _ws_with_covariance_clear(ws, proof=_full_proof())
    assert _run(validator, ["--mode", "strict"]) == 0
    out = json.loads((ws / "output" / "math_estimator_clear_validation.json").read_text())
    assert out["by_status"].get("math_proof_valid") == 1
    assert out["blocking"] == 0


def test_finding_linked_math_item_needs_no_proof(ws):
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        _manifest_item("_calculateQuantAMMCovariance", "QuantAMMCovarianceBasedRule",
                       "for(uint i;i<n;){A[i][j]=lambda.mul(p).div(1e18);}"),
    ]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:QuantAMMCovarianceBasedRule:_calculateQuantAMMCovariance#abcd",
         "status": "cleared", "evidence": ["Cov.sol:47"], "finding_refs": ["H-11"],
         "clear_reason": "captured as a finding"}]})
    assert _run(validator, ["--mode", "strict"]) == 0
    out = json.loads((ws / "output" / "math_estimator_clear_validation.json").read_text())
    assert out["by_status"].get("finding_linked") == 1


def test_non_math_clear_passes(ws):
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        _manifest_item("getOwner", "Pool", "return owner;", score=1),
    ]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Pool:getOwner#abcd", "status": "cleared", "evidence": ["Pool.sol:5"],
         "finding_refs": [], "clear_reason": "view getter, no state write"}]})
    assert _run(validator, ["--mode", "strict"]) == 0
    out = json.loads((ws / "output" / "math_estimator_clear_validation.json").read_text())
    # not math-sensitive → not even listed
    assert out["math_estimator_sensitive_clears"] == 0


# ---------- writer pass-through + downgrade enforcement ----------

def _ws_for_sweep(ws):
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        _manifest_item("_calculateQuantAMMCovariance", "QuantAMMCovarianceBasedRule",
                       "for(uint i;i<n;){A[i][j]=lambda.mul(p).div(1e18);}"),
    ]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:QuantAMMCovarianceBasedRule:_calculateQuantAMMCovariance#abcd",
         "status": "unassigned", "evidence": [], "finding_refs": [], "clear_reason": None}]})


def test_writer_routes_proofless_math_clear_under_full_audit(ws, monkeypatch):
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    _ws_for_sweep(ws)
    # NOTE: clear-text is deliberately free of dependency tokens so the dependency block does not route
    # first; this isolates the MATH-estimator routing path (the policy under test).
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": "function:QuantAMMCovarianceBasedRule:_calculateQuantAMMCovariance#abcd",
         "disposition": "cleared", "evidence_span": "Cov.sol:47",
         "reason": "code agrees with the published model description",
         "attacker_reachability": "only the update runner can call this",
         "guard_or_invariant": "input ranges fixed when the pool is created",
         "no_impact_reason": "outputs stay within the configured numeric range"}]})
    assert _run(sweep_write, []) == 0
    item = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}[
        "function:QuantAMMCovarianceBasedRule:_calculateQuantAMMCovariance#abcd"]
    assert item["status"] == "assigned"
    assert item["assigned_pass"] == "deep"
    assert item["assigned_agent"] == "math_estimator_review"


def test_writer_clears_math_with_valid_proof_under_full_audit(ws, monkeypatch):
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    _ws_for_sweep(ws)
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": "function:QuantAMMCovarianceBasedRule:_calculateQuantAMMCovariance#abcd",
         "disposition": "cleared", "evidence_span": "Cov.sol:47",
         "reason": "re-derived the formula by hand; result agrees with the published model",
         "attacker_reachability": "only the update runner can call this",
         "guard_or_invariant": "input ranges fixed when the pool is created",
         "no_impact_reason": "outputs stay within the configured numeric range",
         "math_estimator_proof": _full_proof()}]})
    assert _run(sweep_write, []) == 0
    item = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}[
        "function:QuantAMMCovarianceBasedRule:_calculateQuantAMMCovariance#abcd"]
    assert item["status"] == "cleared"
    assert item.get("math_estimator_proof", {}).get("math_domain") == "covariance"  # proof preserved


def test_writer_does_not_route_when_math_strict_off(ws, monkeypatch):
    monkeypatch.delenv("AUDITWATCH_FULL_AUDIT", raising=False)
    _ws_for_sweep(ws)
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": "function:QuantAMMCovarianceBasedRule:_calculateQuantAMMCovariance#abcd",
         "disposition": "cleared", "evidence_span": "Cov.sol:47",
         "reason": "estimator math reviewed; formulas match NatSpec",
         "attacker_reachability": "runner-gated", "guard_or_invariant": "lambda in (0,1)",
         "no_impact_reason": "matches sibling rule"}]})
    assert _run(sweep_write, []) == 0
    item = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}[
        "function:QuantAMMCovarianceBasedRule:_calculateQuantAMMCovariance#abcd"]
    assert item["status"] == "cleared"  # not downgraded when math-strict is off


def test_apply_update_preserves_math_proof():
    d = {"manifest_id": "x", "evidence": [], "finding_refs": []}
    errs = ucd.apply_update(d, "cleared", evidence=["A.sol:1"], clear_reason="re-derived",
                            math_estimator_proof=_full_proof())
    assert errs == []
    assert d["math_estimator_proof"]["math_domain"] == "covariance"
