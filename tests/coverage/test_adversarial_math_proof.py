"""
Tests for the ADVERSARIAL math-proof rule + the formula-diff harness (no LLM, no network).

A schema-complete math_estimator_proof is still INVALID if it is merely confirmatory — it restates the
implemented formula and declares it intended, never checking economic direction or attacker-favorable
scaling. This is the Swan/Dria getFee (M-08) / QuantAMM H-11 failure. These tests exercise:
  - validate_proof's confirmatory_proof triggers (#1 match-without-support, #2 "appears intended",
    #3 economic-direction-missing, #4 shift/scale-not-attacker-tested) + the genuine-analysis escape;
  - the writer routing a confirmatory proof to needs_deep_pass under AUDITWATCH_FULL_AUDIT=1;
  - the safe-AST formula-diff harness (divergence / overflow / precision-loss / monotonicity inversion).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
validator = importlib.import_module("validate_math_estimator_clears")
sweep_write = importlib.import_module("coverage_sweep_write")
harness = importlib.import_module("math_formula_diff_harness")


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


def _adversarial_proof(**over):
    """A genuinely adversarial proof (divergence found vs an external source)."""
    p = {"math_domain": "fee_math",
         "intended_formula": "fee = 2 * difficulty",
         "implemented_formula": "fee = 2 << difficulty",
         "formula_source": ["whitepaper"],
         "independent_rederivation": "whitepaper specifies linear scaling; code shifts (exponential)",
         "input_domain": "difficulty 0..32", "output_domain": "uint256 wei",
         "scaling_precision": "no fixed-point; raw shift", "rounding_behavior": "exact integers",
         "signedness_assumptions": "unsigned", "bounds_and_guards": "difficulty bounded by registry",
         "edge_cases_checked": ["difficulty=0", "difficulty=32"], "invariant_preserved": "fee >= base",
         "evidence_span": "Fee.sol:10",
         "formula_diff": "intended doubles linearly; code doubles exponentially via <<",
         "assumptions": ["difficulty set by oracle registry"],
         "monotonicity_and_economic_direction": "fee should grow linearly with difficulty; code grows exponentially",
         "attacker_favorable_search": "swept difficulty to max 32 boundary; 2**33 overflow at the top",
         "economic_impact_if_wrong": "requester massively overpays at high difficulty"}
    p.update(over)
    return p


# ---------- confirmatory_proof triggers ----------

def test_match_without_external_or_economic_is_confirmatory():
    # intended == implemented, formula_source only derived_in_review, no economic analysis
    p = _adversarial_proof(intended_formula="fee = 2 << difficulty",
                           formula_source=["derived_in_review"],
                           monotonicity_and_economic_direction="unchanged",
                           attacker_favorable_search="none",
                           economic_impact_if_wrong="")
    # economic_impact empty -> incomplete first; fill it to isolate the match trigger
    p["economic_impact_if_wrong"] = "n/a"
    status, _, reasons = validator.validate_proof(p)
    assert status == "confirmatory_proof"


def test_match_with_genuine_economic_analysis_is_valid():
    # formulas match, no whitepaper, BUT real economic-direction + attacker search + impact -> valid
    p = _adversarial_proof(intended_formula="fee = 2 << difficulty",
                           formula_source=["derived_in_review"],
                           monotonicity_and_economic_direction="fee rises with difficulty; confirmed monotone, no inversion",
                           attacker_favorable_search="swept difficulty 0..32, max boundary, no overflow within domain",
                           economic_impact_if_wrong="overpay if exponential were unintended")
    assert validator.validate_proof(p)[0] == "math_proof_valid"


def test_appears_intended_language_is_confirmatory():
    p = _adversarial_proof(formula_source=["code"], limitations="x",
                           independent_rederivation="the formula appears intended and matches the code")
    # formula_source code-only with limitations dodges natspec_only; the phrase trigger still fires
    assert validator.validate_proof(p)[0] == "confirmatory_proof"


def test_no_economic_variable_is_confirmatory():
    p = _adversarial_proof(monotonicity_and_economic_direction="the output is bounded and consistent")
    status, _, reasons = validator.validate_proof(p)
    assert status == "confirmatory_proof"
    assert any("economic variable" in r for r in reasons)


def test_shift_without_attacker_extreme_is_confirmatory():
    p = _adversarial_proof(attacker_favorable_search="checked a couple of typical mid-range values")
    status, _, reasons = validator.validate_proof(p)
    assert status == "confirmatory_proof"
    assert any("shift/scaling" in r for r in reasons)


def test_adversarial_off_skips_content_checks():
    p = _adversarial_proof(intended_formula="fee = 2 << difficulty",
                           formula_source=["derived_in_review"],
                           monotonicity_and_economic_direction="unchanged",
                           attacker_favorable_search="none")
    assert validator.validate_proof(p, adversarial=False)[0] == "math_proof_valid"


# ---------- writer routing ----------

def _ws_for_getfee(ws, proof):
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        {"id": "function:LLMOracleManager:getFee#abcd", "kind": "function", "contract": "LLMOracleManager",
         "file": "Fee.sol", "name": "getFee",
         "signature": "function getFee() public { for(uint i;i<n;){fee += diff << difficulty;} }",
         "in_scope": True, "attack_surface_score": 4, "tags": ["fee"],
         "source_span": {"start_line": 1, "end_line": 1}}]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:LLMOracleManager:getFee#abcd", "status": "unassigned",
         "evidence": [], "finding_refs": [], "clear_reason": None}]})
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": "function:LLMOracleManager:getFee#abcd", "disposition": "cleared",
         "evidence_span": "Fee.sol:10", "reason": "fee math re-derived",
         "attacker_reachability": "anyone can read the fee", "guard_or_invariant": "difficulty bounded",
         "no_impact_reason": "within range", "math_estimator_proof": proof}]})


def test_writer_routes_confirmatory_getfee_under_full_audit(ws, monkeypatch):
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    # confirmatory proof: restates the shift formula, no economic direction, no attacker search
    proof = _adversarial_proof(intended_formula="fee = 2 << difficulty",
                               formula_source=["NatSpec", "code"], limitations="no whitepaper",
                               monotonicity_and_economic_direction="output is consistent",
                               attacker_favorable_search="typical values only")
    _ws_for_getfee(ws, proof)
    assert _run(sweep_write, []) == 0
    disp = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}
    item = disp["function:LLMOracleManager:getFee#abcd"]
    assert item["status"] == "assigned"
    assert item["assigned_agent"] == "math_estimator_review"


def test_writer_clears_adversarial_getfee_under_full_audit(ws, monkeypatch):
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    # genuinely adversarial proof that found the divergence is allowed to clear (the reviewer DID the work)
    _ws_for_getfee(ws, _adversarial_proof())
    assert _run(sweep_write, []) == 0
    disp = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}
    assert disp["function:LLMOracleManager:getFee#abcd"]["status"] == "cleared"


# ---------- validator CLI: advisory reports, strict blocks confirmatory ----------

def _confirmatory_proof():
    # restates the implemented formula as intended; no external source, no economic direction
    return _adversarial_proof(intended_formula="A=lambda*A+(p-m)(p-m)'",
                              implemented_formula="A=lambda*A+(p-m)(p-m)'",
                              math_domain="covariance", formula_source=["derived_in_review"],
                              monotonicity_and_economic_direction="output stays consistent",
                              attacker_favorable_search="a few nominal values")


def _ws_with_covariance_clear(ws, proof):
    ws_item = {"id": "function:Rule:_calculateQuantAMMCovariance#c1", "kind": "function", "contract": "Rule",
               "file": "Cov.sol", "name": "_calculateQuantAMMCovariance",
               "signature": "function _calculateQuantAMMCovariance() internal", "in_scope": True,
               "attack_surface_score": 4, "tags": [], "source_span": {}}
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [ws_item]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Rule:_calculateQuantAMMCovariance#c1", "status": "cleared",
         "evidence": ["Cov.sol:5"], "finding_refs": [], "clear_reason": "re-derived",
         "math_estimator_proof": proof}]})


def test_validator_strict_blocks_confirmatory_proof(ws):
    _ws_with_covariance_clear(ws, _confirmatory_proof())
    assert _run(validator, ["--mode", "advisory"]) == 0          # advisory never blocks
    out = json.loads((ws / "output" / "math_estimator_clear_validation.json").read_text())
    assert out["by_status"].get("confirmatory_proof") == 1
    assert _run(validator, ["--mode", "strict"]) == 1            # strict blocks


# ---------- formula-diff harness ----------

def test_harness_detects_getfee_divergence():
    r = harness.run("2*difficulty", "2<<difficulty", {"difficulty": (0, 32)})
    assert r["verdict"] == "divergence_found"
    assert r["divergence"]["count"] > 0
    assert r["divergence"]["max_abs_diff"] > 1000


def test_harness_detects_precision_loss():
    r = harness.run("(a*c)/b", "(a/b)*c", {"a": (1, 100), "b": (1, 10), "c": (1, 10)})
    assert r["precision_loss"]["count"] > 0


def test_harness_detects_monotonicity_inversion():
    r = harness.run("stake", "1000-stake", {"stake": (0, 1000)})
    assert len(r["monotonicity_inversions"]) > 0


def test_harness_detects_underflow():
    r = harness.run("a-b", "a-b", {"a": (0, 10), "b": (0, 10)})
    assert r["overflow"]["count"] > 0  # a-b underflows uint when b>a


def test_harness_no_divergence_on_equivalent_formulas():
    r = harness.run("fee*qty", "qty*fee", {"fee": (0, 1000), "qty": (0, 1000)})
    assert r["verdict"] == "no_divergence"


def test_harness_ast_whitelist_rejects_code():
    with pytest.raises(harness.FormulaError):
        harness.parse_formula("__import__('os').system('echo hi')")
    with pytest.raises(harness.FormulaError):
        harness.parse_formula("x.attr")
