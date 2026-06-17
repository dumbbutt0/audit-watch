"""
Tests for the read-only Evidence Bundle Gate. No LLM, no network.

Covers: a complete record → READY_FOR_REVIEW; an unresolvable location → INSUFFICIENT_EVIDENCE with
missing=[location_resolvable, code_snippet]; missing rationale/evidence → INSUFFICIENT; confidence &
declared_severity_potential carried VERBATIM (never changed); NO bug/severity/exploitability verdict field is
emitted (assemble, don't adjudicate); routing_allowed:false + research_only:true on every bundle; a normalized
input whose routing_allowed is not false is REFUSED; empty input handled; schema-valid; deterministic.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
gate = importlib.import_module("evidence_bundle_gate")

try:
    import jsonschema
    HAVE_JSONSCHEMA = True
except Exception:
    HAVE_JSONSCHEMA = False
SCHEMA = json.loads((ROOT / "schemas" / "evidence_bundle.schema.json").read_text())

# a real, resolvable source location in the repo (the Revert anchor)
REAL_FILE = "audits/revert-lend-2024-03-strict-eval/contracts/2024-03-revert-lend/src/V3Vault.sol"


def _rec(**kw):
    base = dict(candidate_id="permit_asset_binding:V3Vault:_deposit:ab12cd34",
                detector="permit_asset_binding", detector_version="v1", signal_type="asset_binding_missing",
                candidate_surface="V3Vault._deposit", confidence="high", declared_severity_potential="high",
                source_audit_path="x/permit_asset_binding_audit.json",
                file_line_refs=f"{REAL_FILE}:877",
                evidence={"permit_source": "permittransferfrom", "expected_asset_source": "IERC20(asset)",
                          "missing_binding_explanation": "no permitted.token == asset check"},
                routing_allowed=False, research_only=True)
    base.update(kw)
    return base


def _normfile(tmp, records, routing_allowed=False):
    p = tmp / "research_findings_normalized.json"
    p.write_text(json.dumps({"schema_version": "1.0", "routing_allowed": routing_allowed, "records": records,
                             "sources": [], "summary": {}}))
    return p


def _run(tmp, normfile):
    out = tmp / "evidence_bundles.json"
    old = sys.argv
    sys.argv = ["g", "--normalized", str(normfile), "--out", str(out), "--quiet"]
    try:
        assert gate.main() == 0
    finally:
        sys.argv = old
    return json.loads(out.read_text())


# 1. complete record -> READY_FOR_REVIEW with a real snippet
# 2. unresolvable location -> INSUFFICIENT + missing location/snippet
def test_unresolvable_insufficient(tmp_path):
    r = _run(tmp_path, _normfile(tmp_path, [_rec(file_line_refs="nonexistent/File.sol:10")]))
    b = r["bundles"][0]
    assert b["bundle_status"] == "INSUFFICIENT_EVIDENCE"
    assert "code_snippet" in b["evidence_completeness"]["missing"]
    assert b["code_snippet"] is None


# 3. missing rationale + evidence -> INSUFFICIENT
def test_missing_rationale_evidence(tmp_path):
    r = _run(tmp_path, _normfile(tmp_path, [_rec(evidence={})]))
    b = r["bundles"][0]
    assert b["bundle_status"] == "INSUFFICIENT_EVIDENCE"
    assert "evidence_payload" in b["evidence_completeness"]["missing"]
    assert "rationale" in b["evidence_completeness"]["missing"]


# 4. confidence + declared_severity_potential carried VERBATIM (never changed)
def test_verbatim_carry(tmp_path):
    for conf, sev in [("high", "high"), ("medium", "medium"), ("low", "info"), ("needs_context", "medium")]:
        r = _run(tmp_path, _normfile(tmp_path, [_rec(confidence=conf, declared_severity_potential=sev)]))
        b = r["bundles"][0]
        assert b["confidence"] == conf and b["declared_severity_potential"] == sev


# 5. ASSEMBLE-DON'T-ADJUDICATE: no bug/severity/exploitability verdict field emitted
def test_no_verdict_fields(tmp_path):
    r = _run(tmp_path, _normfile(tmp_path, [_rec()]))
    b = r["bundles"][0]
    forbidden = {"is_bug", "severity", "exploitability_score", "recommended_next_step", "verdict", "exploit"}
    assert forbidden.isdisjoint(b.keys())
    # the only recommendation is a completeness one
    assert b["investigate_recommendation"] in ("ready_for_review", "needs_more_evidence")


# 6. routing_allowed false + research_only true on every bundle + top level
def test_flags(tmp_path):
    r = _run(tmp_path, _normfile(tmp_path, [_rec(), _rec(candidate_surface="V3Vault._repay")]))
    assert r["routing_allowed"] is False
    for b in r["bundles"]:
        assert b["routing_allowed"] is False and b["research_only"] is True


# 7. input whose routing_allowed is not false -> refused
def test_refuse_non_research_input(tmp_path):
    nf = _normfile(tmp_path, [_rec()], routing_allowed=True)
    old = sys.argv
    sys.argv = ["g", "--normalized", str(nf), "--out", str(tmp_path / "o.json"), "--quiet"]
    try:
        with pytest.raises(SystemExit):
            gate.main()
    finally:
        sys.argv = old


# 8. empty input handled
def test_empty(tmp_path):
    r = _run(tmp_path, _normfile(tmp_path, []))
    assert r["summary"]["total_bundles"] == 0 and r["bundles"] == []


# 9. schema valid
def test_schema_valid(tmp_path):
    if not HAVE_JSONSCHEMA:
        pytest.skip("jsonschema not installed")
    r = _run(tmp_path, _normfile(tmp_path, [_rec(), _rec(file_line_refs="nope/X.sol:1")]))
    jsonschema.validate(r, SCHEMA)


# 10. deterministic
def test_deterministic(tmp_path):
    nf = _normfile(tmp_path, [_rec()])
    a = _run(tmp_path, nf); b = _run(tmp_path, nf)
    a.pop("generated_at"); b.pop("generated_at")
    assert a == b
