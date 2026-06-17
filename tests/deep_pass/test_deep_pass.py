"""Phase-14 / Experiment E1 — agentic deep-pass triplet (deterministic halves; RESEARCH-ONLY).

Covers the prepare candidate-selection + bundle shape (+ ladder flags), the write --eval validation
(likely_exploitable mandatory evidence, REPRO_HINT presence, dispositions untouched), and the scorer's
ingestion of deep_pass_audit.json by family. No LLM, no network.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
prepare = importlib.import_module("deep_pass_prepare")
dpw = importlib.import_module("deep_pass_write")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


SRC = """// SPDX-License-Identifier: MIT
contract C {
    function calc() public {
        uint x = helper(a);
        total = x;
    }
    function helper(uint a) internal returns (uint) {
        return a + 1;
    }
}
"""


def _src(ws):
    p = ws / "C.sol"
    p.write_text(SRC)
    return str(p)  # absolute → ROOT / abs == abs


def _item(mid, name, contract, file, start, score=2, tags=None, inscope=True, kind="function"):
    return {"id": mid, "kind": kind, "name": name, "contract": contract, "file": file,
            "in_scope": inscope, "attack_surface_score": score, "tags": tags or [],
            "signature": f"function {name}()", "visibility": "public",
            "source_span": {"start_line": start}}


def _manifest(ws, items):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"items": items}))


def _run_prepare(argv):
    old = sys.argv
    sys.argv = ["deep_pass_prepare"] + argv + ["--quiet"]
    try:
        return prepare.main()
    finally:
        sys.argv = old


# ───────────────────────── prepare: selection + bundle shape ─────────────────────────

def test_prepare_selects_routed_highsurface_valuetag_not_lowtail(ws):
    src = _src(ws)
    items = [
        _item("function:C:calc", "calc", "C", src, 3, score=1, tags=[]),          # routed (via detector)
        _item("function:C:big", "big", "C", src, 3, score=5, tags=[]),            # high_surface
        _item("function:C:acc", "acc", "C", src, 3, score=2, tags=["accounting"]),# value_tag
        _item("function:C:low", "low", "C", src, 3, score=1, tags=["config"]),    # excluded (low + non-value tag)
        _item("function:C:oos", "oos", "C", src, 3, score=9, tags=["token"], inscope=False),  # out of scope
        _item("function:C:helper", "helper", "C", src, 7, score=0, tags=[]),      # callee target only
    ]
    _manifest(ws, items)
    # detector output routes 'calc'
    (ws / "output" / "value_flow_parity_audit.json").write_text(json.dumps({
        "lens": "value_flow_parity",
        "candidates": [{"manifest_id": "function:C:calc", "shape": "loop_index_anomaly",
                        "confidence": "low", "contract": "C", "function": "calc"}]}))

    _run_prepare([])
    idx = json.loads((ws / "output" / "deep_pass" / "_bundles" / "index.json").read_text())
    picked = {b["function"] for b in idx["bundles"]}
    assert {"calc", "big", "acc"} <= picked
    assert "low" not in picked and "oos" not in picked
    assert idx["rung"] == "c2"
    # routed reason recorded
    calc = next(b for b in idx["bundles"] if b["function"] == "calc")
    assert "detector_routed" in calc["selected_because"]


def test_prepare_bundle_has_body_callee_and_kb(ws):
    src = _src(ws)
    _manifest(ws, [
        _item("function:C:calc", "calc", "C", src, 3, score=5, tags=["accounting"]),
        _item("function:C:helper", "helper", "C", src, 7, score=0, tags=[]),
    ])
    _run_prepare([])
    bdir = ws / "output" / "deep_pass" / "_bundles"
    calc = next(json.loads(p.read_text()) for p in bdir.glob("dp_*.json")
                if json.loads(p.read_text())["function"] == "calc")
    assert "function calc" in calc["function_body"]
    assert any(c["name"] == "helper" for c in calc["callees"])  # callee resolved
    assert "kb_precedents" in calc  # c2 includes KB


def test_prepare_no_kb_is_c1_and_omits_precedents(ws):
    src = _src(ws)
    _manifest(ws, [_item("function:C:calc", "calc", "C", src, 3, score=5, tags=["accounting"])])
    _run_prepare(["--no-kb"])
    bdir = ws / "output" / "deep_pass" / "_bundles"
    idx = json.loads((bdir / "index.json").read_text())
    assert idx["rung"] == "c1"
    calc = next(json.loads(p.read_text()) for p in bdir.glob("dp_*.json"))
    assert "kb_precedents" not in calc


def test_prepare_package_only_is_c0_and_forbids_reasoning(ws):
    src = _src(ws)
    _manifest(ws, [_item("function:C:calc", "calc", "C", src, 3, score=5, tags=["accounting"])])
    _run_prepare(["--package-only"])
    idx = json.loads((ws / "output" / "deep_pass" / "_bundles" / "index.json").read_text())
    assert idx["rung"] == "c0"
    assert "NO REASONING" in idx["instructions"].upper()


# ───────────────────────── write --eval: validation + research-only ─────────────────────────

def _decisions(ws, decisions):
    p = ws / "output" / "deep_pass" / "_decisions.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"packet_id": "deep_pass_c2", "decisions": decisions}))
    return p


def _good_repro():
    return {"state_preconditions": ["victim owns id"], "required_actor": "EOA",
            "required_assets": ["tokenId"], "critical_transaction": "burn(id)",
            "expected_violation": "tokens removed from wrong account"}


def _eval(ws, dec_path):
    out = ws / "output" / "deep_pass_audit.json"
    dpw._run_eval(dec_path, out, quiet=True)
    return json.loads(out.read_text())


def test_eval_emits_candidates_and_leaves_dispositions_untouched(ws):
    _manifest(ws, [_item("function:C:_burn", "_burn", "C", _src(ws), 3)])
    disp = ws / "output" / "coverage_dispositions.json"
    disp.write_text(json.dumps({"dispositions": [{"manifest_id": "x", "status": "unassigned"}]}))
    before = disp.read_text()
    dp = _decisions(ws, [
        {"manifest_id": "function:C:_burn", "decision": "finding", "family": "value_flow_parity",
         "shape": "identity_resolution_then_misuse", "contract": "VotingEscrow", "function": "_burn",
         "confidence": "high", "evidence_span": "C.sol:4", "repro_hint": _good_repro()},
        {"manifest_id": "function:C:_burn", "decision": "likely_exploitable", "family": "value_flow_parity",
         "contract": "C", "function": "calc", "evidence_span": "C.sol:4",
         "attacker_entrypoint": "calc()", "divergence_point": "C.sol:4", "claimed_effect": "drain",
         "repro_hint": _good_repro()},
        {"manifest_id": "function:C:_burn", "decision": "strong_clear", "contract": "C", "function": "z",
         "evidence_span": "C.sol:4", "attacker_reachability": "n", "guard_or_invariant": "g",
         "no_impact_reason": "view"},
        {"manifest_id": "function:C:_burn", "decision": "needs_human", "contract": "C", "function": "w"},
    ])
    rep = _eval(ws, dp)
    decs = {c["function"]: c for c in rep["candidates"]}
    assert set(decs) == {"_burn", "calc"}            # only finding + likely_exploitable become candidates
    assert decs["_burn"]["confidence"] == "high"
    assert decs["calc"]["confidence"] == "medium"
    assert decs["_burn"]["repro_hint"]["critical_transaction"] == "burn(id)"
    assert rep["research_only"] is True and rep["eval_mode"] is True
    assert disp.read_text() == before               # dispositions byte-identical (untouched)


def test_eval_rejects_likely_exploitable_without_mandatory_evidence(ws):
    _manifest(ws, [_item("function:C:f", "f", "C", _src(ws), 3)])
    dp = _decisions(ws, [
        {"manifest_id": "function:C:f", "decision": "likely_exploitable", "function": "f",
         "evidence_span": "C.sol:4", "repro_hint": _good_repro()}])  # no attacker_entrypoint/claimed_effect
    rep = _eval(ws, dp)
    assert rep["candidates"] == [] and rep["rejected"] == 1


def test_eval_rejects_finding_without_repro_hint(ws):
    _manifest(ws, [_item("function:C:f", "f", "C", _src(ws), 3)])
    dp = _decisions(ws, [
        {"manifest_id": "function:C:f", "decision": "finding", "function": "f",
         "evidence_span": "C.sol:4"}])  # no repro_hint
    rep = _eval(ws, dp)
    assert rep["candidates"] == [] and rep["rejected"] == 1


def test_eval_rejects_finding_without_evidence(ws):
    _manifest(ws, [_item("function:C:f", "f", "C", _src(ws), 3)])
    dp = _decisions(ws, [
        {"manifest_id": "function:C:f", "decision": "finding", "function": "f",
         "repro_hint": _good_repro()}])  # no evidence_span
    rep = _eval(ws, dp)
    assert rep["candidates"] == [] and rep["rejected"] == 1


# ───────────────────────── scorer ingests deep_pass by family ─────────────────────────

