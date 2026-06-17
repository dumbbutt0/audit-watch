"""
Tests for the read-only Research Finding Normalization Layer. No LLM, no network.

Covers: both detector shapes normalize; routing_allowed==false & research_only==true on every record + top level;
a production-routed source is REFUSED; unknown-lens fallback (no crash, info priority); confidence is copied
VERBATIM (never upgraded/downgraded); review_priority ordering is deterministic and permit-high > multicall-medium
at equal confidence; empty/0-candidate input handled; records satisfy the draft-07 schema.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
norm = importlib.import_module("normalize_research_findings")

jsonschema = pytest.importorskip("jsonschema", reason="jsonschema optional") if False else None
try:
    import jsonschema  # noqa: F811
    HAVE_JSONSCHEMA = True
except Exception:
    HAVE_JSONSCHEMA = False

SCHEMA = json.loads((ROOT / "schemas" / "research_finding_normalized.schema.json").read_text())


def _audit(tmp, name, lens, candidates, routed=False):
    rep = {"lens": lens, "is_gate": False, "research_only": True,
           "routes_in_production": routed, "routed_manifest_ids": (["x"] if routed else []),
           "candidates": candidates}
    p = tmp / name
    p.write_text(json.dumps(rep))
    return p


PERMIT_C = {"contract": "V3Vault", "function": "_deposit", "confidence": "high",
            "finding_shape": "permit_asset_binding_missing", "lens_id": "V3Vault:_deposit:permit_asset_binding_missing",
            "permit_source": "permittransferfrom", "expected_asset_source": "IERC20(asset)",
            "missing_binding_explanation": "no permitted.token == asset", "suppression_status": "none",
            "file_line_refs": "V3Vault.sol:877"}
MULTI_C = {"contract": "Multicall", "function": "multicall", "confidence": "high",
           "finding_shape": "delegatecall_self_context", "lens_id": "Multicall:multicall:delegatecall_self_context",
           "invariant_terms": [], "multicall_function": "multicall", "check_location": "in_loop",
           "reason": "delegatecalls address(this) over bytes[]", "file_line_refs": "Multicall.sol:12"}


def _run(tmp, audits):
    out = tmp / "normalized.json"
    old = sys.argv
    sys.argv = ["n"] + sum((["--audit", str(a)] for a in audits), []) + ["--out", str(out), "--quiet"]
    try:
        assert norm.main() == 0
    finally:
        sys.argv = old
    return json.loads(out.read_text())


# 1. both detectors normalize
def test_both_normalize(tmp_path):
    a = _audit(tmp_path, "permit_asset_binding_audit.json", "permit_asset_binding", [PERMIT_C])
    b = _audit(tmp_path, "multicall_invariant_audit.json", "multicall_invariant", [MULTI_C])
    r = _run(tmp_path, [a, b])
    assert r["summary"]["total_records"] == 2
    assert r["summary"]["by_detector"] == {"permit_asset_binding": 1, "multicall_invariant": 1}


# 2. routing_allowed false + research_only true everywhere
def test_flags_forced(tmp_path):
    a = _audit(tmp_path, "permit_asset_binding_audit.json", "permit_asset_binding", [PERMIT_C])
    r = _run(tmp_path, [a])
    assert r["routing_allowed"] is False
    for rec in r["records"]:
        assert rec["routing_allowed"] is False and rec["research_only"] is True


# 3. production-routed source is refused
def test_routed_source_refused(tmp_path):
    a = _audit(tmp_path, "permit_asset_binding_audit.json", "permit_asset_binding", [PERMIT_C], routed=True)
    r = _run(tmp_path, [a])
    assert r["records"] == []
    assert r["sources"][0]["accepted"] is False and "routed" in r["sources"][0]["reason"]


# 4. unknown lens -> fallback, no crash, info severity
def test_unknown_lens_fallback(tmp_path):
    a = _audit(tmp_path, "weird_audit.json", "some_future_detector",
               [{"contract": "C", "function": "f", "confidence": "medium", "finding_shape": "x", "reason": "y"}])
    r = _run(tmp_path, [a])
    rec = r["records"][0]
    assert rec["signal_type"] == "unclassified_research_signal"
    assert rec["declared_severity_potential"] == "info"


# 5. confidence copied VERBATIM (never changed) — hard rule
def test_confidence_never_changed(tmp_path):
    for conf in ["high", "medium", "low", "needs_context"]:
        c = dict(PERMIT_C); c["confidence"] = conf
        a = _audit(tmp_path, "permit_asset_binding_audit.json", "permit_asset_binding", [c])
        r = _run(tmp_path, [a])
        assert r["records"][0]["confidence"] == conf      # identical, not upgraded/downgraded


# 6. review_priority deterministic + permit(high-sev) ranks above multicall(medium-sev) at equal confidence
def test_priority_ordering(tmp_path):
    a = _audit(tmp_path, "permit_asset_binding_audit.json", "permit_asset_binding", [PERMIT_C])     # high conf, high sev
    b = _audit(tmp_path, "multicall_invariant_audit.json", "multicall_invariant", [MULTI_C])         # high conf, medium sev
    r1 = _run(tmp_path, [a, b])
    r2 = _run(tmp_path, [a, b])
    assert [x["candidate_id"] for x in r1["records"]] == [x["candidate_id"] for x in r2["records"]]   # deterministic
    assert r1["records"][0]["detector"] == "permit_asset_binding"                                     # higher sev wins
    assert r1["records"][0]["review_priority"] > r1["records"][1]["review_priority"]
    # why_priority echoes the factors
    assert set(r1["records"][0]["why_priority"]) == {"confidence_weight", "severity_weight", "suppression_penalty"}


# 7. empty / 0-candidate input handled
def test_empty_input(tmp_path):
    a = _audit(tmp_path, "permit_asset_binding_audit.json", "permit_asset_binding", [])
    r = _run(tmp_path, [a])
    assert r["summary"]["total_records"] == 0 and r["sources"][0]["accepted"] is True


# 8. suppression penalty lowers priority (and is recorded)
def test_suppression_penalty(tmp_path):
    c = dict(PERMIT_C); c["suppression_status"] = "router"
    a = _audit(tmp_path, "permit_asset_binding_audit.json", "permit_asset_binding", [c])
    r = _run(tmp_path, [a])
    assert r["records"][0]["why_priority"]["suppression_penalty"] > 0


# 9. records satisfy the draft-07 schema (when jsonschema available)
def test_schema_valid(tmp_path):
    if not HAVE_JSONSCHEMA:
        pytest.skip("jsonschema not installed")
    a = _audit(tmp_path, "permit_asset_binding_audit.json", "permit_asset_binding", [PERMIT_C])
    b = _audit(tmp_path, "multicall_invariant_audit.json", "multicall_invariant", [MULTI_C])
    r = _run(tmp_path, [a, b])
    jsonschema.validate(r, SCHEMA)


# 10. traceability fields present + stable across runs
def test_traceability(tmp_path):
    a = _audit(tmp_path, "permit_asset_binding_audit.json", "permit_asset_binding", [PERMIT_C])
    r1 = _run(tmp_path, [a]); r2 = _run(tmp_path, [a])
    rec = r1["records"][0]
    assert rec["candidate_id"] and rec["source_audit_path"] and rec["detector_version"] == "v1"
    assert rec["schema_version"] == norm.SCHEMA_VERSION
    assert rec["candidate_id"] == r2["records"][0]["candidate_id"]   # deterministic id
