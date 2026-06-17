"""
Tests for the dependency-aware clear policy (no LLM, no network).

A coverage clear may not rely on an UNREVIEWED downstream dependency (guard/estimator/oracle/math-rule/
invariant/lifecycle check). These tests cover dependency_clear_utils classification, the
validate_dependency_clears.py advisory/strict modes, the coverage_sweep_write.py downgrade enforcement,
and backward-compatibility with old dispositions lacking the new fields.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
dcu = importlib.import_module("dependency_clear_utils")
validator = importlib.import_module("validate_dependency_clears")
sweep_write = importlib.import_module("coverage_sweep_write")
gate = importlib.import_module("coverage_completeness_gate")


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


# ---------- unit: classification ----------

def test_no_dependency_language_is_not_dependency_based():
    d = {"status": "cleared", "evidence": ["A.sol:10"],
         "clear_reason": "view getter, returns stored value, no state mutation"}
    assert dcu.is_dependency_based_clear(d) is False
    cls = dcu.classify_clear(d, {}, {})
    assert cls["status"] == "not_dependency_based"


def test_prose_only_guarded_downstream_is_advisory_not_blocking():
    # P177: a prose-only "guarded downstream" mention is detected but is NOT hard-routed (advisory).
    d = {"status": "cleared", "evidence": ["A.sol:10"],
         "clear_reason": "safe because guarded downstream before use"}
    assert dcu.is_dependency_based_clear(d) is True
    assert dcu.dependency_signal_source(d) == "prose"
    cls = dcu.classify_clear(d, {}, {})
    assert cls["status"] == "missing_dependency_metadata"
    assert cls["status"] not in dcu.STRUCTURED_BLOCKING
    assert dcu.dependency_route_decision(cls, d) == "advisory"


def test_guardquantammweights_prose_only_is_advisory():
    # P177: the original QuantAMM over-clearance prose ("outputs pass through _guardQuantAMMWeights") is
    # prose-only → advisory now; the estimator lens (not guarded-downstream) is what catches that surface.
    d = {"status": "cleared", "evidence": ["S.sol:34"],
         "clear_reason": "bounded math; outputs pass through _guardQuantAMMWeights before setWeights"}
    assert dcu.is_dependency_based_clear(d) is True
    cls = dcu.classify_clear(d, {}, {})
    assert cls["status"] == "missing_dependency_metadata"
    assert dcu.dependency_route_decision(cls, d) == "advisory"
    # flag-off restores legacy hard-block on the same prose-only clear
    assert dcu.dependency_route_decision(cls, d, require_structured=False) == "block"


def test_valid_dependency_clear_with_reviewed_dependency_passes():
    # dependency function is itself cleared WITH evidence (reviewed)
    dep_id = "function:Guard:_guardQuantAMMWeights#dead"
    disp_index = {dep_id: {"manifest_id": dep_id, "status": "cleared",
                           "evidence": ["Guard.sol:19 clamp+epsilon"], "clear_reason": "deeply reviewed clamp"}}
    name_index = {"_guardquantammweights": [dep_id]}
    d = {"status": "cleared", "evidence": ["S.sol:34"],
         "clear_reason": "outputs pass through _guardQuantAMMWeights",
         "clear_depends_on": [dep_id],
         "dependency_clearance_status": "all_cleared",
         "dependency_reason": "guard clamps weights to rails before use; guard is itself reviewed",
         "dependency_evidence": ["Guard.sol:19-30"]}
    cls = dcu.classify_clear(d, disp_index, name_index)
    assert cls["status"] == "dependency_valid"
    assert cls["computed_clearance"] in dcu.DEP_CLEARANCE_OK


def test_complete_structured_unreviewed_dependency_blocks():
    # P177 genuine hard-route: COMPLETE structured metadata (all 4 dep fields) resolving to an in-scope,
    # unreviewed dependency. This is the only shape that still hard-routes under require_structured.
    dep_id = "function:Guard:_guardQuantAMMWeights#dead"
    disp_index = {dep_id: {"manifest_id": dep_id, "status": "assigned", "assigned_pass": "deep"}}
    name_index = {"_guardquantammweights": [dep_id]}
    d = {"status": "cleared", "evidence": ["S.sol:34"],
         "clear_reason": "outputs pass through _guardQuantAMMWeights",
         "clear_depends_on": [dep_id], "downstream_guard_claim": True,
         "dependency_clearance_status": "unreviewed_dependency",
         "dependency_reason": "guard clamps", "dependency_evidence": ["Guard.sol:19"]}
    cls = dcu.classify_clear(d, disp_index, name_index)
    assert cls["status"] == "unreviewed_dependency"
    assert cls["status"] in dcu.STRUCTURED_BLOCKING
    assert dcu.dependency_route_decision(cls, d) == "block"


def test_out_of_scope_dependency_is_allow():
    # P177: an auditor-declared out-of-scope dependency does not meet the "in-scope unproven guard" bar.
    d = {"status": "cleared", "evidence": ["S.sol:34"], "downstream_guard_claim": True,
         "clear_reason": "leans on external registry guard", "dependency_scope": "out_of_scope"}
    cls = dcu.classify_clear(d, {}, {})
    assert cls["status"] == "out_of_scope_dependency"
    assert dcu.dependency_route_decision(cls, d) == "allow"


def test_valid_proof_status_is_allow():
    # P177: a dependency carrying a valid proof is closed (non-blocking).
    d = {"status": "cleared", "evidence": ["S.sol:34"], "downstream_guard_claim": True,
         "clear_reason": "leans on _guardQuantAMMWeights clamp", "proof_status": "valid"}
    cls = dcu.classify_clear(d, {}, {})
    assert cls["status"] == "dependency_valid"
    assert dcu.dependency_route_decision(cls, d) == "allow"


# ---------- integration: validator advisory vs strict ----------

def _ws_with_one_dependency_clear(ws):
    # P177 genuine blocking case: COMPLETE structured metadata leaning on an in-scope UNREVIEWED guard.
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        {"id": "function:Pool:pack#aaaa", "kind": "function", "contract": "Pool",
         "file": "Pool.sol", "name": "pack", "in_scope": True, "attack_surface_score": 2,
         "tags": [], "source_span": {}},
        {"id": "function:Guard:_guard#bbbb", "kind": "function", "contract": "Guard",
         "file": "Guard.sol", "name": "_guard", "in_scope": True, "attack_surface_score": 2,
         "tags": [], "source_span": {}},
    ]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Pool:pack#aaaa", "status": "cleared", "evidence": ["Pool.sol:5"],
         "finding_refs": [], "clear_reason": "bounded math; clamped by _guard downstream",
         "clear_depends_on": ["function:Guard:_guard#bbbb"], "downstream_guard_claim": True,
         "dependency_clearance_status": "unreviewed_dependency",
         "dependency_reason": "leans on _guard clamp", "dependency_evidence": ["Guard.sol:1"]},
        {"manifest_id": "function:Guard:_guard#bbbb", "status": "assigned", "assigned_pass": "deep",
         "evidence": [], "finding_refs": []},
    ]})


def _ws_with_prose_only_clear(ws):
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        {"id": "function:Pool:pack#aaaa", "kind": "function", "contract": "Pool",
         "file": "Pool.sol", "name": "pack", "in_scope": True, "attack_surface_score": 2,
         "tags": [], "source_span": {}},
    ]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Pool:pack#aaaa", "status": "cleared", "evidence": ["Pool.sol:5"],
         "finding_refs": [], "clear_reason": "bounded math; clamped by _guardQuantAMMWeights downstream"},
    ]})


def test_validator_advisory_exits_zero_but_reports(ws, capsys):
    _ws_with_one_dependency_clear(ws)
    rc = _run(validator, ["--mode", "advisory"])
    assert rc == 0
    out = json.loads((ws / "output" / "dependency_clear_validation.json").read_text())
    assert out["dependency_based_clears"] == 1
    assert out["blocking"] == 1


def test_validator_strict_exits_nonzero(ws):
    _ws_with_one_dependency_clear(ws)
    rc = _run(validator, ["--mode", "strict"])
    assert rc == 1


def test_validator_prose_only_clear_is_not_blocking(ws):
    # P177: a prose-only dependency clear is advisory → validator reports it dependency-based but NOT blocking.
    _ws_with_prose_only_clear(ws)
    rc = _run(validator, ["--mode", "strict"])
    assert rc == 0
    out = json.loads((ws / "output" / "dependency_clear_validation.json").read_text())
    assert out["dependency_based_clears"] == 1
    assert out["blocking"] == 0


# ---------- integration: writer downgrade enforcement ----------

def test_writer_downgrades_structured_unreviewed_clear_in_full_audit(ws, monkeypatch):
    # P177: a COMPLETE structured clear resolving an in-scope UNREVIEWED guard still hard-routes in full audit.
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        {"id": "function:Pool:pack#aaaa", "kind": "function", "contract": "Pool",
         "file": "Pool.sol", "name": "pack", "in_scope": True, "attack_surface_score": 2,
         "tags": [], "source_span": {}},
        {"id": "function:Guard:_guard#bbbb", "kind": "function", "contract": "Guard",
         "file": "Guard.sol", "name": "_guard", "in_scope": True, "attack_surface_score": 2,
         "tags": [], "source_span": {}},
    ]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Pool:pack#aaaa", "status": "unassigned", "evidence": [],
         "finding_refs": [], "clear_reason": None},
        {"manifest_id": "function:Guard:_guard#bbbb", "status": "assigned", "assigned_pass": "deep",
         "evidence": [], "finding_refs": []},
    ]})
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": "function:Pool:pack#aaaa", "disposition": "cleared", "evidence_span": "Pool.sol:5",
         "reason": "bounded; leans on _guard", "clear_depends_on": ["function:Guard:_guard#bbbb"],
         "downstream_guard_claim": True, "dependency_clearance_status": "unreviewed_dependency",
         "dependency_reason": "leans on _guard clamp", "dependency_evidence": ["Guard.sol:1"]},
    ]})
    rc = _run(sweep_write, [])
    assert rc == 0
    disp = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}
    item = disp["function:Pool:pack#aaaa"]
    assert item["status"] == "assigned"
    assert item["assigned_pass"] == "deep"
    assert item.get("dependency_review_required") is True
    assert _run(gate, ["--quiet"]) == 1


def test_writer_prose_only_clear_stays_cleared_advisory_in_full_audit(ws, monkeypatch):
    # P177 core behavior change: a PROSE-ONLY guarded-downstream clear is NOT hard-routed even in full audit;
    # it stays cleared with an advisory flag (no deep-pass flooding).
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        {"id": "function:Pool:pack#aaaa", "kind": "function", "contract": "Pool",
         "file": "Pool.sol", "name": "pack", "in_scope": True, "attack_surface_score": 2,
         "tags": [], "source_span": {}},
    ]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Pool:pack#aaaa", "status": "unassigned", "evidence": [],
         "finding_refs": [], "clear_reason": None},
    ]})
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": "function:Pool:pack#aaaa", "disposition": "cleared",
         "evidence_span": "Pool.sol:5", "reason": "bounded; guarded downstream by _guardQuantAMMWeights"},
    ]})
    assert _run(sweep_write, []) == 0
    disp = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}
    item = disp["function:Pool:pack#aaaa"]
    assert item["status"] == "cleared"                       # NOT routed
    assert item.get("dependency_review_required") is True    # advisory flag only
    assert "P177" in (item.get("routed_reason") or "")


def test_writer_nonstrict_allows_clear_but_annotates(ws, monkeypatch):
    # default config: dependency_clear_strict false and no full-audit env → clear proceeds (advisory).
    monkeypatch.delenv("AUDITWATCH_FULL_AUDIT", raising=False)
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        {"id": "function:Pool:pack#aaaa", "kind": "function", "contract": "Pool",
         "file": "Pool.sol", "name": "pack", "in_scope": True, "attack_surface_score": 2,
         "tags": [], "source_span": {}},
    ]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Pool:pack#aaaa", "status": "unassigned", "evidence": [],
         "finding_refs": [], "clear_reason": None},
    ]})
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": "function:Pool:pack#aaaa", "disposition": "cleared",
         "evidence_span": "Pool.sol:5", "reason": "bounded; guarded downstream by _guardQuantAMMWeights"},
    ]})
    assert _run(sweep_write, []) == 0
    disp = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}
    item = disp["function:Pool:pack#aaaa"]
    assert item["status"] == "cleared"  # not downgraded in non-strict
    assert item.get("dependency_review_required") is True  # but flagged advisory


# ---------- backward compatibility ----------

def test_old_disposition_without_new_fields_does_not_crash():
    old = {"manifest_id": "x", "status": "cleared", "evidence": ["A.sol:1"],
           "clear_reason": "view function, no state write"}  # no dependency_* fields at all
    cls = dcu.classify_clear(old, {}, {})
    assert cls["status"] == "not_dependency_based"
    assert dcu.check_dependency_metadata(old) == dcu.required_dependency_fields()  # all missing, but no crash


# ---------- finding-linked escape (non-blocking when the clear cites an existing finding) ----------

def test_dependency_clear_with_finding_refs_is_non_blocking():
    # dependency language present, but the clear is anchored to a filed finding via finding_refs
    d = {"status": "cleared", "evidence": ["A.sol:10"], "finding_refs": ["DT-003"],
         "clear_reason": "safe because guarded downstream before use"}
    assert dcu.is_dependency_based_clear(d) is True
    cls = dcu.classify_clear(d, {}, {})
    assert cls["status"] == "finding_linked_dependency"
    assert cls["status"] not in dcu.BLOCKING_CLASSIFICATIONS


def test_dependency_clear_citing_DT003_in_reason_is_non_blocking():
    d = {"status": "cleared", "evidence": ["A.sol:10"],
         "clear_reason": "risk lives in onAfterRemoveLiquidity, already filed as DT-003; guarded downstream"}
    cls = dcu.classify_clear(d, {}, {})
    assert cls["status"] == "finding_linked_dependency"
    assert cls["clearance_status"] == "finding_linked"


def test_dependency_clear_citing_DPF036_is_non_blocking():
    d = {"status": "cleared", "evidence": ["A.sol:10"],
         "clear_reason": "bounded math; guarded downstream — same root cause as DPF-036"}
    assert dcu.classify_clear(d, {}, {})["status"] == "finding_linked_dependency"


def test_guarded_downstream_without_finding_link_is_not_finding_linked():
    # no finding link → not the finding-linked escape; classifies as missing_dependency_metadata (advisory P177)
    d = {"status": "cleared", "evidence": ["A.sol:10"],
         "clear_reason": "safe because guarded downstream before use"}
    cls = dcu.classify_clear(d, {}, {})
    assert cls["status"] == "missing_dependency_metadata"
    assert dcu.dependency_route_decision(cls, d) == "advisory"
    # a standard/token id (ERC-20) must NOT be misread as a finding link
    d2 = {"status": "cleared", "evidence": ["A.sol:10"],
          "clear_reason": "safe because guarded downstream; handles ERC-20 tokens"}
    assert dcu.classify_clear(d2, {}, {})["status"] == "missing_dependency_metadata"


def test_apply_update_stores_p177_capture_fields():
    ucd = importlib.import_module("update_coverage_disposition")
    d = {"manifest_id": "x", "evidence": [], "finding_refs": []}
    errs = ucd.apply_update(d, "cleared", evidence=["A.sol:1"], clear_reason="reviewed",
                            dependency_name="_guard", dependency_scope="in_scope",
                            dependency_status="unreviewed_dependency", proof_status="missing")
    assert errs == []
    assert d["dependency_name"] == "_guard"
    assert d["dependency_scope"] == "in_scope"
    assert d["dependency_status"] == "unreviewed_dependency"
    assert d["proof_status"] == "missing"


def test_generic_tokens_not_extracted_as_dependency_names():
    d = {"status": "cleared",
         "clear_reason": "require(msg.sender==x); zero address check; path validated downstream by guard"}
    names = [n.lower() for n in dcu.extract_dependency_names(d)]
    for g in ("require", "zero", "path", "check", "validate", "guard", "downstream"):
        assert g not in names


def test_phrase_detection_survives_stoplist():
    # "guarded downstream" still classifies as dependency-based, but yields no generic dependency name
    d = {"status": "cleared", "clear_reason": "safe because guarded downstream"}
    assert dcu.is_dependency_based_clear(d) is True
    assert dcu.extract_dependency_names(d) == []
