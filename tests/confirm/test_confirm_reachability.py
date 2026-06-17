"""
Tests for the reachability-truth confirm pass (analyzer + gate) — deterministic, no LLM/network.

The precision lever: classify whether an unprivileged attacker can drive a candidate to impact. Verifies the
honest-classification rules (downgrade/flag, never auto-confirm or auto-FP a speculative finding) and the
dual-mode gate (eval never blocks; submission hard-fails non-credible confirmed claims). Mirrors
tests/migration_flow.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
reach = importlib.import_module("confirm_reachability")
gate = importlib.import_module("confirm_gate")


def _ws(tmp_path, monkeypatch, manifest_items, candidates, dispositions=None):
    (tmp_path / "output" / "confirm").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"items": manifest_items}))
    (tmp_path / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": dispositions or []}))
    (tmp_path / "output" / "confirm" / "confirm_inventory.json").write_text(
        json.dumps({"candidates": candidates}))
    return tmp_path


def _fn(name, vis="external", kind="function", mut="", mods=None, file="contracts/A.sol", in_scope=True):
    return {"id": f"function:A:{name}#x", "kind": kind, "name": name, "visibility": vis, "mutability": mut,
            "modifiers": mods or [], "file": file, "in_scope": in_scope, "source_span": {"start_line": 1}}


def _cand(fid, fns, sev="High", layer="merged", cls=None, refs=("function:A:x#x",), impact="loss", entry=None,
          dup=None, consumer=False):
    return {"finding_id": fid, "title": fid, "severity": sev, "layer": layer, "classification": cls,
            "affected_functions": fns, "manifest_refs": list(refs), "claimed_entrypoint": entry or (fns[0] if fns else ""),
            "claimed_sink": fns[0] if fns else "", "claimed_sink_file": "", "claimed_impact": impact,
            "existing_confidence": "Medium", "consumer_found": consumer,
            "source_evidence": {}, "duplicate_relationships": [dup] if dup else [],
            "required_confirmation_fields": {"present": [], "missing": []}}


def _run_reach(tmp_path):
    old = sys.argv
    sys.argv = ["confirm_reachability"]
    try:
        assert reach.main() == 0
    finally:
        sys.argv = old
    return {x["finding_id"]: x for x in
            json.loads((tmp_path / "output" / "confirm" / "reachability_analysis.json").read_text())["results"]}


def _status(tmp_path, monkeypatch, items, cands, disp=None):
    _ws(tmp_path, monkeypatch, items, cands, disp)
    return _run_reach(tmp_path)


# ── analyzer classification cases ──
def test_external_no_blocker_likely_reachable(tmp_path, monkeypatch):
    r = _status(tmp_path, monkeypatch, [_fn("withdrawAll", vis="external")],
                [_cand("F1", ["withdrawAll"], impact="drains funds")])
    assert r["F1"]["reachability_status"] == "likely_reachable"


def test_internal_sink_with_public_caller_likely(tmp_path, monkeypatch):
    items = [_fn("_doThing", vis="internal"), _fn("doThing", vis="external")]
    r = _status(tmp_path, monkeypatch, items, [_cand("F2", ["_doThing"], entry="doThing", consumer=True, impact="steals")])
    assert r["F2"]["reachability_status"] in ("likely_reachable", "uncertain")


def test_internal_sink_no_callers_dead_path(tmp_path, monkeypatch):
    items = [_fn("_orphan", vis="internal", in_scope=True)]
    disp = [{"manifest_id": "function:A:_orphan#x", "status": "deferred_out_of_scope"}]
    r = _status(tmp_path, monkeypatch, items, [_cand("F3", ["_orphan"], consumer=False)], disp)
    assert r["F3"]["reachability_status"] == "dead_path"
    assert r["F3"]["suggested_action"] == "mark_false_positive"


def test_only_owner_privileged_only(tmp_path, monkeypatch):
    r = _status(tmp_path, monkeypatch, [_fn("setFee", vis="external", mods=["onlyOwner"])],
                [_cand("F4", ["setFee"], impact="wrong fee")])
    assert r["F4"]["reachability_status"] == "privileged_only"


def test_initializer_only_lifecycle(tmp_path, monkeypatch):
    r = _status(tmp_path, monkeypatch, [_fn("init", kind="initializer", file="contracts/reseed/ReseedSilo.sol")],
                [_cand("F5", ["init"])])
    assert r["F5"]["reachability_status"] == "lifecycle_only"


def test_governance_only_privileged(tmp_path, monkeypatch):
    r = _status(tmp_path, monkeypatch, [_fn("setParam", vis="external", mods=["onlyGovernance"])],
                [_cand("F6", ["setParam"])])
    assert r["F6"]["reachability_status"] == "privileged_only"


def test_missing_manifest_refs_insufficient(tmp_path, monkeypatch):
    r = _status(tmp_path, monkeypatch, [_fn("foo")], [_cand("F7", ["foo"], refs=())])
    assert r["F7"]["reachability_status"] == "insufficient_evidence"


def test_duplicate_root_cause(tmp_path, monkeypatch):
    r = _status(tmp_path, monkeypatch, [_fn("bar")], [_cand("F8", ["bar"], dup="OTHER-001")])
    assert r["F8"]["reachability_status"] == "duplicate"
    assert r["F8"]["suggested_action"] == "merge_duplicate"


def test_speculative_needs_runtime_poc(tmp_path, monkeypatch):
    r = _status(tmp_path, monkeypatch, [_fn("gm", vis="external")],
                [_cand("F9", ["gm"], impact="underflow reverts season advancement if ratio drops below 1e4")])
    assert r["F9"]["suggested_action"] == "needs_runtime_poc"


# ── gate cases ──
def _run_gate(tmp_path, monkeypatch, results, candidates, mode, strict=False):
    (tmp_path / "output" / "confirm").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    (tmp_path / "output" / "confirm" / "reachability_analysis.json").write_text(json.dumps({"results": results}))
    (tmp_path / "output" / "confirm" / "confirm_inventory.json").write_text(json.dumps({"candidates": candidates}))
    old = sys.argv
    sys.argv = ["confirm_gate", "--mode", mode, "--quiet"] + (["--strict"] if strict else [])
    try:
        return gate.main()
    finally:
        sys.argv = old


def test_high_privileged_fails_submission(tmp_path, monkeypatch):
    results = [{"finding_id": "H1", "severity": "High", "reachability_status": "privileged_only", "suggested_action": "downgrade"}]
    cands = [{"finding_id": "H1", "layer": "merged", "classification": None}]
    assert _run_gate(tmp_path, monkeypatch, results, cands, "submission") == 1


def test_eval_mode_never_blocks(tmp_path, monkeypatch):
    results = [{"finding_id": "U1", "severity": "High", "reachability_status": "uncertain", "suggested_action": "needs_runtime_poc"},
               {"finding_id": "P1", "severity": "High", "reachability_status": "privileged_only", "suggested_action": "downgrade"}]
    cands = [{"finding_id": "U1", "layer": "eval", "classification": "partial_eval_finding"},
             {"finding_id": "P1", "layer": "merged", "classification": None}]
    assert _run_gate(tmp_path, monkeypatch, results, cands, "eval") == 0  # advisory only


def test_partial_eval_finding_warns_not_blocks_submission(tmp_path, monkeypatch):
    # a partial_eval_finding self-declares non-confirmed -> warns, does not hard-fail submission
    results = [{"finding_id": "E1", "severity": "High", "reachability_status": "insufficient_evidence", "suggested_action": "needs_manual_review"}]
    cands = [{"finding_id": "E1", "layer": "eval", "classification": "partial_eval_finding"}]
    assert _run_gate(tmp_path, monkeypatch, results, cands, "submission") == 0
