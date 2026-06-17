"""P108: adversarial self-kill — RESEARCH-ONLY, un-wired.

Proves the self-kill layer emits ONLY the 4 allowed states, kills only on a source-PROVABLE defense (dispositive
guard, or multi-primitive full coverage with no consequence), never kills a confirmed PoC or on uncertainty, routes
cross-contract to NEEDS_RUNTIME, sets no severity/submission/validation state, and is deterministic. The live corpus
asserts the SAFETY invariants (no awarded finding killed, P104 survives) — not a kill-power pass, which the corpus
honestly does not achieve from source alone.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import self_kill_validation as SK  # noqa: E402

CORPUS = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"

_FIXTURE = (
    "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.0;\n"
    "contract C {\n"
    "  mapping(address=>uint256) public bal; uint256 public total; address owner; address seller;\n"
    "  function withdrawAll() external { bal[msg.sender]+=1; total+=1; IERC20(t).transfer(msg.sender, total); }\n"
    "  function buy(uint256 id) external { require(msg.sender != seller, \"no self buy\"); bal[msg.sender]+=id; }\n"
    "  function sync() external { uint256 p = IOracle(o).price(); total = p; pool.staticcall(d); }\n"
    "  function poke(uint256 x) external { require(x <= limit); cfg = x; }\n"
    "}\n"
)


def _corpus(tmp_path, with_poc=True):
    (tmp_path / "C.sol").write_text(_FIXTURE, encoding="utf-8")
    awarded = [
        {"finding_id": "AWD", "contract": "C", "function": "withdrawAll",
         "invariant_category": "per_user_accounting", "severity": "High", "surfaceable": True, "grounding": "high"},
    ]
    if with_poc:
        awarded.append({"finding_id": "AWD-XC", "contract": "C", "function": "sync",
                        "invariant_category": "cross_contract_consistency", "severity": "Medium",
                        "surfaceable": True, "grounding": "high",
                        "conversion": {"poc_succeeded": True, "evidence_ref": "fixture"}})
    return {"exclude_substrings": [],
            "subjects": [{"id": "fx", "phase": "test", "source_roots": [str(tmp_path)], "awarded_findings": awarded}]}


def test_flags_unwired():
    assert SK.FLAGS["is_gate"] is False
    assert SK.FLAGS["research_only"] is True
    assert SK.FLAGS["routes_in_production"] is False
    assert SK.FLAGS["routed_manifest_ids"] == []


def test_self_test_passes():
    assert SK._self_test() == 0


def test_only_four_states_exist():
    assert SK.STATES == {"KILLED", "SURVIVED", "NEEDS_RUNTIME", "NEEDS_CONTEXT"}


def test_dispositive_guard_kills():
    r = SK.self_kill({"subject": "x", "contract": "C", "function": "buy",
                      "body": 'function buy(uint256 id) external { require(msg.sender != seller); bal[msg.sender]+=id; }',
                      "features": {"actor_clarity": 1.0}, "is_awarded": False, "is_confirmed_poc": False})
    assert r["state"] == "KILLED" and r["kill_basis"] == "dispositive_guard"


def test_confirmed_poc_never_killed():
    r = SK.self_kill({"subject": "x", "contract": "C", "function": "f", "body": "function f() external {}",
                      "features": {}, "is_awarded": True, "is_confirmed_poc": True})
    assert r["state"] == "SURVIVED"


def test_cross_contract_unconfirmed_needs_runtime():
    r = SK.self_kill({"subject": "x", "contract": "C", "function": "sync2",
                      "body": "function sync2() external { uint256 p = IOracle(o).price(); total=p; pool.staticcall(d); }",
                      "features": {"exploitability_external_call": 1.0, "actor_clarity": 1.0},
                      "declared_category": "cross_contract_consistency", "is_awarded": False, "is_confirmed_poc": False})
    assert r["state"] == "NEEDS_RUNTIME"


def test_no_body_needs_context():
    r = SK.self_kill({"subject": "x", "contract": "C", "function": "g", "body": "",
                      "features": {}, "is_awarded": False, "is_confirmed_poc": False})
    assert r["state"] == "NEEDS_CONTEXT"


def test_single_primitive_coverage_does_not_kill():
    """negative_space (single relevant primitive) reaching COVERS off one state-update must NOT be a kill —
    this is the SS-M-11 spotPurchase false-kill guard."""
    body = "function setThing(uint256 x) external { bought += x; }"  # state update -> negative_space 'COVERS', 1 primitive
    r = SK.self_kill({"subject": "x", "contract": "C", "function": "setThing", "body": body,
                      "features": {"actor_clarity": 1.0}, "is_awarded": False, "is_confirmed_poc": False})
    assert r["state"] != "KILLED", "single-primitive coverage must not produce a kill"


def test_no_promotion_or_severity_fields(tmp_path):
    res = SK.run_corpus(_corpus(tmp_path))
    assert SK.assert_states_only(res)


def test_kills_are_defense_proven_not_uncertainty(tmp_path):
    res = SK.run_corpus(_corpus(tmp_path))
    for c in res["candidates"]:
        if c["state"] == "KILLED":
            assert c["kill_basis"] in ("dispositive_guard", "covered_and_inert")
            assert not c["runtime_required"], "a killed candidate must not be runtime-required"


def test_deterministic(tmp_path):
    corpus = _corpus(tmp_path)
    a, b = SK.run_corpus(corpus), SK.run_corpus(corpus)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def _sources_present():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    return all(Path(r).exists() for s in corpus["subjects"] for r in s["source_roots"])


@pytest.mark.skipif(not _sources_present(), reason="burned /tmp subject sources not present")
def test_live_safety_invariants_hold():
    """The hard-stops the spec requires: P104 survives, no awarded finding killed, all hard-stops clear, 4 states."""
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    res = SK.run_corpus(corpus)
    gt = res["ground_truth"]
    assert gt["p104_state"] == "SURVIVED", "P104 must survive"
    assert gt["awarded_killed_count"] == 0, "no awarded finding may be killed"
    assert all(not h["tripped"] for h in res["hard_stops"].values()), "no hard stop may trip"
    assert all(c["state"] in SK.STATES for c in res["candidates"])
    assert res["verdict"]["safety_pass"] is True
    assert SK.assert_states_only(res)
