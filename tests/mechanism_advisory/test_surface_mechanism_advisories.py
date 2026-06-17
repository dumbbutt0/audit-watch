"""P135 — tests for surface_mechanism_advisories (advisory routing, no detector logic).

No protocol-specific strings. Validates: per-detector normalization, status preservation, config gates,
dedup, candidate attach, caps, no-confirmed/submission_ready, H-03 deep-pass recommendation.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import surface_mechanism_advisories as s  # noqa: E402

CFG = dict(s.DEFAULT_CFG)
EVAL_CFG = {**CFG, "surface_research_only_advisories": True, "mechanism_advisory_standalone_queue": True}


def _norm(detector, raw_list):
    return s.normalize_hits(detector, raw_list, "aud", f"output/{detector}_audit.json")


# 1. connector_position_accounting -> advisory entry
def test_cpa_entry():
    e = _norm("connector_position_accounting",
              [{"contract": "C", "name": "_getPositionTVL", "file": "C.sol", "shape": "position_tvl_product_div",
                "confidence": "medium", "reason": "div by weight twice"}])
    assert len(e) == 1 and e[0]["detector_status"] == "advisory"
    assert e[0]["mechanism_class"] == "position_tvl_product_div" and e[0]["confidence"] == "medium"
    assert e[0]["advisory_only"] is True and e[0]["submission_ready"] is False


# 2. arithmetic_conservation -> advisory entry
def test_ac_entry():
    e = _norm("arithmetic_conservation",
              [{"contract": "C", "name": "totalLpBalanceOf", "file": "C.sol", "shape": "supply_aggregate",
                "confidence": "medium"}])
    assert e[0]["source_detector"] == "arithmetic_conservation" and e[0]["detector_status"] == "advisory"


# 3. units_invariant report-only -> submission_ready False
def test_units_report_only_not_submission_ready():
    e = _norm("units_invariant",
              [{"contract": "O", "name": "getValue", "file": "O.sol", "category": "chainlink_decimals",
                "high_risk": True, "risk_tags": ["oracle"], "line": 90}])
    assert e[0]["detector_status"] == "report_only" and e[0]["submission_ready"] is False
    assert e[0]["confidence"] == "high"  # derived from high_risk


# 4. semantic_tvl_completeness research-only preserved
def test_stc_research_only_preserved():
    e = _norm("semantic_tvl_completeness",
              [{"connector_contract": "A", "tvl_function": "_getPositionTVL", "file": "A.sol",
                "finding_shape": "omitted_external_stake_balance", "confidence": "high"}])
    assert e[0]["detector_status"] == "research_only"


# 5. master gate disables all
def test_master_gate_disables(tmp_path):
    rep = s.build({**CFG, "surface_mechanism_advisories": False}, tmp_path, "aud", [], [])
    assert rep["surfaced"] is False and rep["advisories"] == []


# 6. research-only excluded unless surface_research_only_advisories
def test_research_only_excluded_by_default():
    e = _norm("semantic_tvl_completeness",
              [{"connector_contract": "A", "tvl_function": "f", "file": "A.sol", "finding_shape": "x"}])
    assert s.apply_status_gate(e, CFG) == []                 # research-only off
    assert len(s.apply_status_gate(e, EVAL_CFG)) == 1        # research-only on


# 7. dedup by file+contract+function+mechanism+detector
def test_dedup():
    raw = [{"contract": "C", "name": "f", "file": "C.sol", "shape": "s", "confidence": "low"}] * 2
    e = _norm("connector_position_accounting", raw)
    assert len(s.dedup(e)) == 1


# 8. attach to existing candidate
def test_attach_to_candidate():
    e = _norm("connector_position_accounting",
              [{"contract": "C", "name": "withdraw", "file": "path/C.sol", "shape": "s", "confidence": "low"}])
    merged = [{"id": "F-001", "location": {"file": "src/C.sol", "function": "withdraw"}}]
    n = s.attach_candidates(e, merged)
    assert n == 1 and e[0]["related_candidate_id"] == "F-001"


# 9. standalone queue entry is advisory_only + requires_human_review (end-to-end)
def test_standalone_queue_entry(tmp_path, monkeypatch):
    out = tmp_path / "output"; out.mkdir()
    (out / "connector_position_accounting_audit.json").write_text(json.dumps(
        {"detected": [{"contract": "C", "name": "f", "file": "C.sol", "shape": "s", "confidence": "high"}]}))
    rep = s.build(EVAL_CFG, out, "aud", [], [])
    assert rep["advisories"][0]["advisory_only"] is True
    assert rep["advisories"][0]["requires_human_review"] is True


# 10. no entry marked confirmed or submission_ready
def test_no_confirmed_or_submission_ready(tmp_path):
    out = tmp_path / "output"; out.mkdir()
    for det, spec in s.DETECTOR_SPECS.items():
        (out / spec["output"]).write_text(json.dumps(
            {spec["key"]: [{spec["contract"]: "C", spec["function"]: "f", "file": "C.sol",
                            spec["mechanism"]: "m", "confidence": "high", "high_risk": True}]}))
    rep = s.build(EVAL_CFG, out, "aud", [], [])
    for e in rep["advisories"]:
        assert e["submission_ready"] is False and e["advisory_only"] is True
        assert "severity" not in e                       # no severity assigned from advisory evidence
        # no status/verdict field claims the item is confirmed
        for k in ("status", "verdict", "confirmed", "triage_status"):
            assert str(e.get(k, "")).lower() != "confirmed"


# 11. caps respected
def test_caps():
    raw = [{"contract": "C", "name": f"f{i}", "file": "C.sol", "shape": "s", "confidence": "low"} for i in range(20)]
    e = _norm("connector_position_accounting", raw)
    capped = s.apply_caps(e, {**CFG, "mechanism_advisory_max_per_detector": 3, "mechanism_advisory_max_total": 40})
    assert len(capped) == 3
    # total cap across detectors
    many = e + _norm("arithmetic_conservation", raw)
    capped2 = s.apply_caps(many, {**CFG, "mechanism_advisory_max_per_detector": 10, "mechanism_advisory_max_total": 5})
    assert len(capped2) == 5


# 12. H-03 oracle/value loop -> deep_pass_value_provenance recommendation (no finding)
def test_deep_pass_recommendation():
    items = [{"kind": "function", "contract": "Oracle", "name": "_getValue", "tags": ["oracle", "token"],
              "file": "Oracle.sol", "source_span": {"start_line": 1, "end_line": 6}}]
    src = ("function _getValue() {\n  for (uint i; i < n; i++) {\n    v = conv(asset, src[i], v);\n"
           "  }\n  return v;\n}\n")
    recs = s.recommend_deep_pass(items, lambda f, a, b: src, cap=10)
    assert len(recs) == 1
    r = recs[0]
    assert r["recommended_prompt"] == "deep_pass_value_provenance"
    assert r["advisory_only"] is True and r["submission_ready"] is False
    assert "severity" not in r and r["mechanism_class"] == "value_provenance_loop"


def test_deep_pass_no_loop_no_rec():
    items = [{"kind": "function", "contract": "O", "name": "f", "tags": ["oracle"], "file": "O.sol",
              "source_span": {"start_line": 1, "end_line": 3}}]
    recs = s.recommend_deep_pass(items, lambda f, a, b: "function f() { return x; }", cap=10)
    assert recs == []
