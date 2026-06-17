"""
Task 2 (special-focus strong clear) + Task 3 (advisory escalation):
- A THIN clear (only the 3 legacy strong fields) on a special-focus function → needs_deep_pass.
- A FULL deep strong clear on the same function → cleared.
- A non-special-focus low-surface function thin clear → cleared (unchanged).
- A high-risk advisory-lens hit on a currently-cleared high-risk surface → re-routed to needs_deep_pass;
  a non-high-risk surface is left untouched; override downgrades to advisory-only.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
sweep_write = importlib.import_module("coverage_sweep_write")
esc = importlib.import_module("advisory_escalation_gate")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "coverage_sweep").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    return tmp_path


def _item(contract, name, sig, score, mid):
    return {"id": mid, "kind": "function", "contract": contract, "file": f"{contract}.sol",
            "name": name, "signature": sig, "in_scope": True, "attack_surface_score": score,
            "tags": [], "source_span": {}}


def _manifest(ws, items):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "source": {}, "items": items}))


def _dispositions(ws, items, status="unassigned"):
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps(
        {"dispositions": [{"manifest_id": i["id"], "status": status} for i in items]}))


def _decisions(ws, decisions):
    (ws / "data" / "coverage_sweep" / "_decisions.json").write_text(json.dumps({"decisions": decisions}))


def _run_sweep():
    old = sys.argv
    sys.argv = ["coverage_sweep_write"]
    try:
        return sweep_write.main()
    finally:
        sys.argv = old


def _status(ws, mid):
    d = json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]
    return next(x["status"] for x in d if x["manifest_id"] == mid)


THIN = {"attacker_reachability": "any validator", "guard_or_invariant": "nonReentrant",
        "no_impact_reason": "the withdrawn amount equals msg.sender's own collateral; no other balance changes"}
DEEP = dict(THIN, attacker_entrypoint="leave() by a validator", cross_function_consumers="addBootstrap, kill",
            downstream_sinks="collateralSource.transferFunds", state_transition_ordering="effects before interaction",
            value_source_consistency="amount from collateral, paid from collateralSource (consistent)",
            reentrancy_callback_analysis="nonReentrant covers leave; siblings reviewed",
            queue_liveness_analysis="no batch/queue in this function")


# ---------- Task 2 ----------

def test_thin_clear_on_special_focus_routed_to_deep_pass(ws):
    it = _item("SubnetActor", "leave", "function leave() external nonReentrant { collateralSource.transferFunds(x); }", 5, "function:SubnetActor:leave#01")
    _manifest(ws, [it]); _dispositions(ws, [it])
    _decisions(ws, [dict(manifest_id=it["id"], disposition="cleared", evidence_span="SubnetActor.sol:1-5",
                         reason="leave is bounded", **THIN)])
    _run_sweep()
    assert _status(ws, it["id"]) == "assigned"          # routed to needs_deep_pass (incomplete_strong_clear)


def test_full_deep_clear_on_special_focus_clears(ws):
    it = _item("SubnetActor", "leave", "function leave() external nonReentrant { collateralSource.transferFunds(x); }", 5, "function:SubnetActor:leave#01")
    _manifest(ws, [it]); _dispositions(ws, [it])
    _decisions(ws, [dict(manifest_id=it["id"], disposition="cleared", evidence_span="SubnetActor.sol:1-5",
                         reason="leave fully analysed", **DEEP)])
    _run_sweep()
    assert _status(ws, it["id"]) == "cleared"


def test_non_special_focus_thin_clear_unchanged(ws):
    it = _item("Misc", "getThing", "function getThing() view returns (uint) { return x; }", 0, "function:Misc:getThing#01")
    _manifest(ws, [it]); _dispositions(ws, [it])
    _decisions(ws, [dict(manifest_id=it["id"], disposition="cleared", evidence_span="Misc.sol:1-2",
                         reason="pure getter, no state mutation")])
    _run_sweep()
    assert _status(ws, it["id"]) == "cleared"


# ---------- Task 3 ----------

def _esc_setup(ws, item, status, lens_high_risk_ids):
    _manifest(ws, [item])
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps(
        {"dispositions": [{"manifest_id": item["id"], "status": status}]}))
    (ws / "output" / "checkpoint_liveness_audit.json").write_text(json.dumps(
        {"lens": "checkpoint_liveness", "high_risk_manifest_ids": lens_high_risk_ids}))


def _run_esc():
    old = sys.argv
    sys.argv = ["advisory_escalation_gate", "--quiet"]
    try:
        return esc.main()
    finally:
        sys.argv = old


def test_high_risk_hit_on_cleared_high_risk_surface_routed(ws):
    it = _item("CheckpointingFacet", "execBottomUpMsgs", "function execBottomUpMsgs() {}", 4, "function:CheckpointingFacet:execBottomUpMsgs#01")
    _esc_setup(ws, it, "cleared", [it["id"]])
    assert _run_esc() == 0
    assert _status(ws, it["id"]) == "assigned"          # cleared → needs_deep_pass


def test_non_high_risk_surface_untouched(ws):
    it = _item("MathLib", "avg", "function avg(uint a, uint b) pure returns (uint) {}", 4, "function:MathLib:avg#01")
    _esc_setup(ws, it, "cleared", [it["id"]])           # lens flagged it, but surface has no high-risk term
    assert _run_esc() == 0
    assert _status(ws, it["id"]) == "cleared"           # untouched (surface not high-risk)


def test_already_finding_not_re_routed(ws):
    it = _item("CheckpointingFacet", "execBottomUpMsgs", "function execBottomUpMsgs() {}", 4, "function:CheckpointingFacet:execBottomUpMsgs#01")
    _esc_setup(ws, it, "finding", [it["id"]])
    assert _run_esc() == 0
    assert _status(ws, it["id"]) == "finding"           # only currently-cleared items are re-routed


def test_override_downgrades_to_advisory(ws, monkeypatch):
    monkeypatch.setenv("AUDITWATCH_ADVISORY_ESCALATION_OVERRIDE", "1")
    it = _item("CheckpointingFacet", "execBottomUpMsgs", "function execBottomUpMsgs() {}", 4, "function:CheckpointingFacet:execBottomUpMsgs#01")
    _esc_setup(ws, it, "cleared", [it["id"]])
    assert _run_esc() == 0
    assert _status(ws, it["id"]) == "cleared"           # override → advisory only
    rep = json.loads((ws / "output" / "advisory_escalation_gate.json").read_text())
    assert rep["override_active"] is True and rep["escalated"] == 1
