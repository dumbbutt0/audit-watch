"""
Fixture tests for the deterministic coverage system (no LLM, no network).

Each test redirects the active-audit workspace to a tmp dir by monkeypatching
audit_context.get_audit_root, then drives the real scripts' main() functions. Covers acceptance
criteria B (manifest), C (dispositions), D (block on unassigned), E (pass when resolved),
F (cleared-without-evidence fails), G (finding-without-ref fails), I (metrics).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
build_manifest = importlib.import_module("build_coverage_manifest")
init_disp = importlib.import_module("init_coverage_dispositions")
gate = importlib.import_module("coverage_completeness_gate")
metrics = importlib.import_module("coverage_metrics")
deep_queue = importlib.import_module("deep_pass_queue")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    """A temp audit workspace; (output dir pre-created)."""
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


# --- acceptance B: manifest builder on a minimal source tree ---
def test_manifest_builder_minimal(ws):
    src = ws / "src"
    src.mkdir()
    (src / "Vault.sol").write_text(
        "// SPDX-License-Identifier: MIT\n"
        "pragma solidity ^0.8.20;\n"
        "contract Vault {\n"
        "    uint256 public constant FEE_BPS = 30;\n"
        "    function deposit(uint256 amount) external {\n"
        "        balances[msg.sender] += amount;\n"
        "    }\n"
        "    function _internalHelper() internal view returns (uint256) {\n"
        "        return 1;\n"
        "    }\n"
        "}\n"
    )
    _write(ws, "output/static.json", {"contract_path": str(src), "functions": [],
                                       "external_calls": [], "tainted_sinks": [], "slither_findings": []})
    rc = _run(build_manifest, ["--contract", str(src)])
    assert rc == 0
    man = json.loads((ws / "output" / "coverage_manifest.json").read_text())
    kinds = {i["kind"] for i in man["items"]}
    names = {i["name"] for i in man["items"]}
    assert man["items"], "manifest must be non-empty"
    assert "function" in kinds and "constant" in kinds
    assert "deposit" in names and "FEE_BPS" in names


def _manifest_one_inscope(ws):
    _write(ws, "output/coverage_manifest.json", {
        "schema_version": 1, "source": {}, "items": [
            {"id": "function:Vault:deposit#aaaa", "kind": "function", "contract": "Vault",
             "file": "src/Vault.sol", "name": "deposit", "in_scope": True,
             "attack_surface_score": 4, "tags": ["accounting"], "source_span": {}},
            {"id": "function:Mock:foo#bbbb", "kind": "function", "contract": "Mock",
             "file": "mocks/Mock.sol", "name": "foo", "in_scope": False,
             "scope_reason": "mock", "attack_surface_score": 0, "tags": [], "source_span": {}},
        ]})


# --- acceptance C + D: dispositions init, then gate blocks on unassigned ---
def test_init_then_gate_blocks_unassigned(ws):
    _manifest_one_inscope(ws)
    assert _run(init_disp, []) == 0
    disp = json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]
    assert len(disp) == 2
    by = {d["manifest_id"]: d["status"] for d in disp}
    assert by["function:Vault:deposit#aaaa"] == "unassigned"
    assert by["function:Mock:foo#bbbb"] == "deferred_out_of_scope"  # out-of-scope auto-deferred
    assert _run(gate, ["--quiet"]) == 1  # unassigned in-scope item blocks


# --- acceptance E: all resolved -> pass ---
def test_gate_passes_when_resolved(ws):
    _manifest_one_inscope(ws)  # in-scope item is score 4 → needs a strong clear
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Vault:deposit#aaaa", "status": "cleared",
         "evidence": ["src/Vault.sol:5 require(amount>0)"], "finding_refs": [],
         "clear_reason": "input-validated, no attacker path", "scope_reason": None,
         "attacker_reachability": "external; require(amount>0) bounds input",
         "guard_or_invariant": "balance accounting invariant",
         "no_impact_reason": "cannot write other accounts"},
        {"manifest_id": "function:Mock:foo#bbbb", "status": "deferred_out_of_scope",
         "evidence": [], "finding_refs": [], "clear_reason": None, "scope_reason": "mock"},
    ]})
    assert _run(gate, ["--quiet"]) == 0
    assert _run(metrics, ["--quiet"]) == 0  # acceptance I
    m = json.loads((ws / "output" / "coverage_metrics.json").read_text())
    assert m["coverage_percent"] == 100.0
    assert m["in_scope_items"] == 1


# --- acceptance F: cleared without evidence -> fail ---
def test_cleared_without_evidence_fails(ws):
    _manifest_one_inscope(ws)
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Vault:deposit#aaaa", "status": "cleared",
         "evidence": [], "finding_refs": [], "clear_reason": "looks fine"},
        {"manifest_id": "function:Mock:foo#bbbb", "status": "deferred_out_of_scope",
         "scope_reason": "mock"},
    ]})
    assert _run(gate, ["--quiet"]) == 1


# --- acceptance G: finding without finding_ref -> fail ---
def test_finding_without_ref_fails(ws):
    _manifest_one_inscope(ws)
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Vault:deposit#aaaa", "status": "finding",
         "evidence": [], "finding_refs": [], "clear_reason": None},
        {"manifest_id": "function:Mock:foo#bbbb", "status": "deferred_out_of_scope",
         "scope_reason": "mock"},
    ]})
    assert _run(gate, ["--quiet"]) == 1


# --- finding WITH ref passes ---
def test_finding_with_ref_passes(ws):
    _manifest_one_inscope(ws)
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Vault:deposit#aaaa", "status": "finding",
         "evidence": ["src/Vault.sol:5"], "finding_refs": ["LG-001"], "clear_reason": None},
        {"manifest_id": "function:Mock:foo#bbbb", "status": "deferred_out_of_scope",
         "scope_reason": "mock"},
    ]})
    assert _run(gate, ["--quiet"]) == 0


# --- high-score (>=3) cleared WITHOUT strong fields is blocked by the gate ---
def test_high_score_weak_clear_blocked(ws):
    # the in-scope item in _manifest_one_inscope has attack_surface_score 4
    _manifest_one_inscope(ws)
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Vault:deposit#aaaa", "status": "cleared",
         "evidence": ["src/Vault.sol:5"], "clear_reason": "looks fine", "finding_refs": []},
        {"manifest_id": "function:Mock:foo#bbbb", "status": "deferred_out_of_scope", "scope_reason": "mock"},
    ]})
    assert _run(gate, ["--quiet"]) == 1  # missing attacker_reachability/guard_or_invariant/no_impact_reason


# --- deep_pass_queue clusters needs_deep_pass items into specialist packets ---
def test_deep_pass_queue_clusters(ws):
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [
        {"id": "fn:LibUsdOracle:getPrice#1", "kind": "function", "contract": "LibUsdOracle",
         "file": "libraries/Oracle/LibUsdOracle.sol", "name": "getPrice", "in_scope": True,
         "attack_surface_score": 5, "tags": ["oracle"], "source_span": {}},
        {"id": "fn:BeanL1RecieverFacet:recieveL1Beans#2", "kind": "function", "contract": "BeanL1RecieverFacet",
         "file": "beanstalk/migration/BeanL1RecieverFacet.sol", "name": "recieveL1Beans", "in_scope": True,
         "attack_surface_score": 5, "tags": ["migration"], "source_span": {}},
        {"id": "fn:Vault:view#3", "kind": "function", "contract": "Vault", "file": "Vault.sol",
         "name": "view", "in_scope": True, "attack_surface_score": 1, "tags": [], "source_span": {}},
    ]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "fn:LibUsdOracle:getPrice#1", "status": "assigned", "assigned_pass": "deep",
         "assigned_agent": "oracle"},
        {"manifest_id": "fn:BeanL1RecieverFacet:recieveL1Beans#2", "status": "assigned",
         "assigned_pass": "deep", "assigned_agent": "cross_chain"},
        {"manifest_id": "fn:Vault:view#3", "status": "cleared", "evidence": ["Vault.sol:1"],
         "clear_reason": "view"},
    ]})
    assert _run(deep_queue, []) == 0
    q = json.loads((ws / "output" / "deep_pass_queue.json").read_text())
    assert q["summary"]["needs_deep_pass_total"] == 2  # the cleared one is excluded
    labels = {c["label"] for c in q["clusters"]}
    assert "oracle_accounting" in labels
    assert "cross_chain_bridge_message_validation" in labels
    # priority-sorted: oracle_accounting (P1) before cross_chain (P2)
    assert q["clusters"][0]["priority"] <= q["clusters"][-1]["priority"]


# --- high-score cleared WITH the 3 strong fields passes ---
def test_high_score_strong_clear_passes(ws):
    _manifest_one_inscope(ws)
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:Vault:deposit#aaaa", "status": "cleared",
         "evidence": ["src/Vault.sol:5"], "clear_reason": "input-validated",
         "attacker_reachability": "external but require(amount>0) at L5",
         "guard_or_invariant": "nonReentrant + balance invariant",
         "no_impact_reason": "cannot exceed own balance; no cross-account write",
         "finding_refs": []},
        {"manifest_id": "function:Mock:foo#bbbb", "status": "deferred_out_of_scope", "scope_reason": "mock"},
    ]})
    assert _run(gate, ["--quiet"]) == 0
