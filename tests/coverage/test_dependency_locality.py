"""
Tests for the dependency-clear LOCALITY / path-dominance rule (no LLM, no network).

A clear that leans on a guard in a DIFFERENT function/contract is only valid if that guard DOMINATES
every attacker-reachable path to the cleared item. A guard "somewhere" is not a guard "on every path"
(Swan/Dria H-02: Swan.purchase's missing local round check was cleared by leaning on BuyerAgent's phase
guard in another contract, but purchase is directly callable). These tests cover:
  - field-presence gate (non-local guard needs guard_locality + path_dominance_evidence + alt paths);
  - the call-graph disproof (a public sink directly callable bypassing the guard → blocked);
  - a genuinely dominating cross-contract guard passing;
  - same-function/local guards never over-blocked;
  - proxy/router alternative-path bypass;
  - the sweep writer routing guard_not_path_dominant to needs_deep_pass under full-audit.
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
sweep_write = importlib.import_module("coverage_sweep_write")


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


def _item(contract, name, vis="external", mid=None):
    return {"id": mid or f"function:{contract}:{name}#0001", "kind": "function", "contract": contract,
            "file": f"{contract}.sol", "name": name, "visibility": vis, "in_scope": True,
            "attack_surface_score": 4, "tags": [], "source_span": {}}


def _reviewed_guard_disp(guard_id):
    return {guard_id: {"manifest_id": guard_id, "status": "cleared", "evidence": ["G.sol:5 checks round"],
                       "clear_reason": "round-phase guard, deeply reviewed"}}


# Sink = Swan.purchase (external, directly callable); guard = BuyerAgent.getRoundPhase (other contract).
SINK_ID = "function:Swan:purchase#s001"
GUARD_ID = "function:BuyerAgent:getRoundPhase#g001"


def _sink_clear(**over):
    d = {"manifest_id": SINK_ID, "status": "cleared", "evidence": ["Swan.sol:120"],
         "clear_reason": "round/phase validated by BuyerAgent.getRoundPhase before purchase",
         "clear_depends_on": [GUARD_ID], "dependency_clearance_status": "all_cleared",
         "dependency_reason": "the phase guard rejects stale-round purchases", "dependency_evidence": ["BuyerAgent.sol:340"],
         "downstream_guard_claim": True, "downstream_guard_type": "lifecycle_check"}
    d.update(over)
    return d


def _ctx():
    manifest_index = {SINK_ID: _item("Swan", "purchase", "external", SINK_ID),
                      GUARD_ID: _item("BuyerAgent", "getRoundPhase", "public", GUARD_ID)}
    name_index = dcu.build_manifest_name_index(list(manifest_index.values()))
    return manifest_index, name_index, _reviewed_guard_disp(GUARD_ID)


# ---------- field-presence gate ----------

def test_nonlocal_guard_without_dominance_fields_blocks():
    mi, ni, disp_index = _ctx()
    d = _sink_clear()  # no guard_locality / path_dominance_evidence / alternative_paths_considered
    cls = dcu.classify_clear(d, disp_index, ni, manifest_index=mi)
    assert cls["status"] == "guard_not_path_dominant"
    assert cls["status"] in dcu.LOCALITY_BLOCKING


def test_nonlocal_guard_declared_nonlocal_blocks():
    mi, ni, disp_index = _ctx()
    d = _sink_clear(guard_locality="non_local", path_dominance_evidence="n/a",
                    alternative_paths_considered="n/a")
    assert dcu.classify_clear(d, disp_index, ni, manifest_index=mi)["status"] == "guard_not_path_dominant"


# ---------- call-graph disproof (the H-02 shape) ----------

def test_public_sink_directly_callable_disproves_dominance():
    mi, ni, disp_index = _ctx()
    # reviewer ASSERTS dominance, but purchase is external and the call graph shows no guard on its path
    d = _sink_clear(guard_locality="cross_contract_dominates",
                    path_dominance_evidence="claims every purchase routes through getRoundPhase",
                    alternative_paths_considered="claims none")
    call_graph = {"call_graph": [
        {"caller_contract": "BuyerAgent", "caller_function": "purchaseFlow",
         "callee_contract": "BuyerAgent", "callee_function": "getRoundPhase"},
        # purchase is NOT called by getRoundPhase; it's directly reachable as a public entry
    ]}
    cls = dcu.classify_clear(d, disp_index, ni, manifest_index=mi, call_graph=call_graph)
    assert cls["status"] == "guard_not_path_dominant"
    assert "disproves dominance" in (cls["locality_reason"] or "")


def test_proxy_router_alternative_path_disproves_dominance():
    # sink is internal (not a self-entry), but a public router reaches it without the guard
    sink_id = "function:Vault:_apply#v1"
    guard_id = "function:Manager:validateRound#m1"
    mi = {sink_id: _item("Vault", "_apply", "internal", sink_id),
          guard_id: _item("Manager", "validateRound", "public", guard_id),
          "r": _item("Router", "execute", "external", "r")}
    ni = dcu.build_manifest_name_index(list(mi.values()))
    disp_index = _reviewed_guard_disp(guard_id)
    d = {"manifest_id": sink_id, "status": "cleared", "evidence": ["Vault.sol:9"],
         "clear_reason": "guarded by Manager.validateRound", "clear_depends_on": [guard_id],
         "dependency_clearance_status": "all_cleared", "dependency_reason": "validates round",
         "dependency_evidence": ["Manager.sol:5"], "downstream_guard_claim": True,
         "guard_locality": "cross_contract_dominates", "path_dominance_evidence": "claims all paths guarded",
         "alternative_paths_considered": "missed the router"}
    call_graph = {"call_graph": [
        {"caller_contract": "Manager", "caller_function": "validateRound",
         "callee_contract": "Vault", "callee_function": "_apply"},
        {"caller_contract": "Router", "caller_function": "execute",
         "callee_contract": "Vault", "callee_function": "_apply"},  # bypass: router → sink, no guard
    ]}
    cls = dcu.classify_clear(d, disp_index, ni, manifest_index=mi, call_graph=call_graph)
    assert cls["status"] == "guard_not_path_dominant"


# ---------- genuinely dominating guard passes ----------

def test_dominating_internal_sink_passes():
    # sink internal, reachable ONLY through the guard (guard → sink edge); no bypass entry
    sink_id = "function:Vault:_apply#v1"
    guard_id = "function:Manager:validateRound#m1"
    mi = {sink_id: _item("Vault", "_apply", "internal", sink_id),
          guard_id: _item("Manager", "validateRound", "public", guard_id)}
    ni = dcu.build_manifest_name_index(list(mi.values()))
    disp_index = _reviewed_guard_disp(guard_id)
    d = {"manifest_id": sink_id, "status": "cleared", "evidence": ["Vault.sol:9"],
         "clear_reason": "guarded by Manager.validateRound", "clear_depends_on": [guard_id],
         "dependency_clearance_status": "all_cleared", "dependency_reason": "validates round before applying",
         "dependency_evidence": ["Manager.sol:5"], "downstream_guard_claim": True,
         "guard_locality": "cross_contract_dominates",
         "path_dominance_evidence": "the only caller of Vault._apply is Manager.validateRound (call graph)",
         "alternative_paths_considered": "no proxy/router/callback path; _apply is internal"}
    call_graph = {"call_graph": [
        {"caller_contract": "Manager", "caller_function": "validateRound",
         "callee_contract": "Vault", "callee_function": "_apply"},
    ]}
    cls = dcu.classify_clear(d, disp_index, ni, manifest_index=mi, call_graph=call_graph)
    assert cls["status"] == "dependency_valid"


def test_sink_that_calls_guard_itself_is_dominated():
    # sink is public but calls the guard in its own body (edge sink → guard) → locally protected
    mi, ni, disp_index = _ctx()
    d = _sink_clear(guard_locality="cross_contract_dominates",
                    path_dominance_evidence="purchase() calls getRoundPhase() at its top",
                    alternative_paths_considered="no other entry")
    call_graph = {"call_graph": [
        {"caller_contract": "Swan", "caller_function": "purchase",
         "callee_contract": "BuyerAgent", "callee_function": "getRoundPhase"},
    ]}
    assert dcu.classify_clear(d, disp_index, ni, manifest_index=mi, call_graph=call_graph)["status"] == "dependency_valid"


# ---------- local guards are never over-blocked ----------

def test_same_function_guard_not_treated_as_nonlocal():
    # the "guard" resolves to the SAME function as the sink → local → no dominance requirement
    mi = {SINK_ID: _item("Swan", "purchase", "external", SINK_ID)}
    ni = dcu.build_manifest_name_index(list(mi.values()))
    d = {"manifest_id": SINK_ID, "status": "cleared", "evidence": ["Swan.sol:120"],
         "clear_reason": "purchase() has a local require(round==current) guard",
         "clear_depends_on": [SINK_ID], "dependency_clearance_status": "all_cleared",
         "dependency_reason": "local round check", "dependency_evidence": ["Swan.sol:121"],
         "downstream_guard_claim": True}
    assert dcu.classify_clear(d, {}, ni, manifest_index=mi)["status"] == "dependency_valid"


def test_locality_skipped_without_manifest_index():
    # backward-compat: no manifest_index → locality not evaluated, prior behavior preserved
    mi, ni, disp_index = _ctx()
    d = _sink_clear()
    assert dcu.classify_clear(d, disp_index, ni)["status"] == "dependency_valid"


# ---------- validator CLI: advisory reports, strict blocks non-dominant ----------

def test_validator_strict_blocks_nondominant_clear(ws, monkeypatch):
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")  # makes dependency_locality_strict_full_audit effective
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        _item("Swan", "purchase", "external", SINK_ID),
        _item("BuyerAgent", "getRoundPhase", "public", GUARD_ID)]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": GUARD_ID, "status": "cleared", "evidence": ["BuyerAgent.sol:340"],
         "finding_refs": [], "clear_reason": "phase guard reviewed"},
        _sink_clear(guard_locality="cross_contract_dominates",
                    path_dominance_evidence="claims all purchases routed through the guard",
                    alternative_paths_considered="claims none")]})
    _write(ws, "data/interactions/call_graph.json", {"call_graph": [
        {"caller_contract": "BuyerAgent", "caller_function": "flow",
         "callee_contract": "BuyerAgent", "callee_function": "getRoundPhase"}]})
    validator = importlib.import_module("validate_dependency_clears")
    assert _run(validator, ["--mode", "advisory"]) == 0
    out = json.loads((ws / "output" / "dependency_clear_validation.json").read_text())
    assert out["locality_enforced"] is True
    assert out["by_status"].get("guard_not_path_dominant") == 1
    assert _run(validator, ["--mode", "strict"]) == 1


# ---------- writer routing ----------

def test_writer_routes_nondominant_clear_under_full_audit(ws, monkeypatch):
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        _item("Swan", "purchase", "external", SINK_ID),
        _item("BuyerAgent", "getRoundPhase", "public", GUARD_ID)]})
    # guard is reviewed (cleared with evidence) so the only block is locality
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": GUARD_ID, "status": "cleared", "evidence": ["BuyerAgent.sol:340"],
         "finding_refs": [], "clear_reason": "phase guard reviewed"},
        {"manifest_id": SINK_ID, "status": "unassigned", "evidence": [], "finding_refs": [], "clear_reason": None}]})
    _write(ws, "data/interactions/call_graph.json", {"call_graph": [
        {"caller_contract": "BuyerAgent", "caller_function": "flow",
         "callee_contract": "BuyerAgent", "callee_function": "getRoundPhase"}]})
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": SINK_ID, "disposition": "cleared", "evidence_span": "Swan.sol:120",
         "reason": "round validated by BuyerAgent.getRoundPhase",
         "attacker_reachability": "buyer calls purchase", "guard_or_invariant": "phase guard in BuyerAgent",
         "no_impact_reason": "stale rounds rejected",
         "clear_depends_on": [GUARD_ID], "dependency_clearance_status": "all_cleared",
         "dependency_reason": "phase guard", "dependency_evidence": ["BuyerAgent.sol:340"],
         "downstream_guard_claim": True,
         "guard_locality": "cross_contract_dominates",
         "path_dominance_evidence": "claims all purchases routed through the guard",
         "alternative_paths_considered": "claims none"}]})
    assert _run(sweep_write, []) == 0
    disp = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}
    item = disp[SINK_ID]
    assert item["status"] == "assigned"
    assert item["assigned_agent"] == "dependency_review"
    assert item.get("dependency_review_required") is True
