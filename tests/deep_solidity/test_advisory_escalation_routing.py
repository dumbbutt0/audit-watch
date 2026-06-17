"""
Task 1 (conversion engine) — advisory escalation must ROUTE high-risk hits, not just thin-cleared ones.

The Panoptic eval found 17 high-risk advisory hits but routed 0 because the gate only re-routed items
whose status was already `cleared`. The 17 were `unassigned`/`assigned`, so nothing converted. These
tests prove high-risk hits on any NON-terminal status now become needs_deep_pass with full provenance,
that low-risk surfaces are never touched (FP control), and that advisory mode only warns.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
esc = importlib.import_module("advisory_escalation_gate")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    return tmp_path


def _item(contract, name, sig, score, mid):
    return {"id": mid, "kind": "function", "contract": contract, "file": f"{contract}.sol",
            "name": name, "signature": sig, "in_scope": True, "attack_surface_score": score,
            "tags": [], "source_span": {}}


def _setup(ws, item, status, lens="checkpoint_liveness", extra_disp=None):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps(
        {"schema_version": 1, "source": {}, "items": [item]}))
    disp = {"manifest_id": item["id"], "status": status}
    if extra_disp:
        disp.update(extra_disp)
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": [disp]}))
    (ws / "output" / f"{lens}_audit.json").write_text(json.dumps(
        {"lens": lens, "high_risk_manifest_ids": [item["id"]]}))


def _run():
    old = sys.argv
    sys.argv = ["advisory_escalation_gate", "--quiet"]
    try:
        return esc.main()
    finally:
        sys.argv = old


def _disp(ws, mid):
    d = json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]
    return next(x for x in d if x["manifest_id"] == mid)


def test_unassigned_high_risk_hit_routes_to_deep_pass(ws):
    """The core Panoptic fix: a high-risk hit on an UNASSIGNED item now converts to needs_deep_pass."""
    it = _item("CollateralTracker", "withdraw", "function withdraw(uint256 a) external {}", 4,
               "function:CollateralTracker:withdraw#01")
    _setup(ws, it, "unassigned")
    assert _run() == 0
    d = _disp(ws, it["id"])
    assert d["status"] == "assigned" and d["assigned_pass"] == "deep"
    # full provenance recorded
    prov = d["advisory_escalation"]
    assert prov["source_lens"] == "checkpoint_liveness"
    assert prov["matched_term"]                       # at least one HIGH_RISK term ("withdraw")
    assert prov["file"] == "CollateralTracker.sol" and prov["function"] == "withdraw"
    assert prov["required_specialist"] == "dos"       # checkpoint_liveness → dos
    rep = json.loads((ws / "output" / "advisory_escalation_gate.json").read_text())
    assert rep["routed_to_deep_pass"] == 1


def test_examined_high_risk_hit_routes(ws):
    it = _item("RiskEngine", "collateralRefund", "function collateralRefund() external {}", 4,
               "function:RiskEngine:collateralRefund#01")
    _setup(ws, it, "examined", lens="recipient_custody")
    # recipient_custody uses a different key shape
    (ws / "output" / "recipient_custody_audit.json").write_text(json.dumps(
        {"routed_to_bridge_custody_review": [it["id"]]}))
    assert _run() == 0
    d = _disp(ws, it["id"])
    assert d["status"] == "assigned" and d["assigned_pass"] == "deep"
    assert d["advisory_escalation"]["required_specialist"] == "access_control"


def test_low_risk_surface_never_routed(ws):
    """FP control: a lens hit on a surface with no high-risk term stays put (and never becomes a finding)."""
    it = _item("MathLib", "avg", "function avg(uint a, uint b) pure returns (uint) {}", 4,
               "function:MathLib:avg#01")
    _setup(ws, it, "unassigned")
    assert _run() == 0
    d = _disp(ws, it["id"])
    assert d["status"] == "unassigned"
    assert d.get("status") != "finding"


def test_justified_high_risk_hit_skipped(ws):
    it = _item("CollateralTracker", "withdraw", "function withdraw(uint256 a) external {}", 4,
               "function:CollateralTracker:withdraw#01")
    _setup(ws, it, "cleared", extra_disp={"advisory_escalation_justified": True,
                                           "advisory_escalation_justification": "reviewed under DPF-007"})
    assert _run() == 0
    assert _disp(ws, it["id"])["status"] == "cleared"


def test_advisory_mode_warns_only(ws, monkeypatch):
    monkeypatch.delenv("AUDITWATCH_FULL_AUDIT", raising=False)
    it = _item("CollateralTracker", "withdraw", "function withdraw(uint256 a) external {}", 4,
               "function:CollateralTracker:withdraw#01")
    _setup(ws, it, "unassigned")
    assert _run() == 0
    assert _disp(ws, it["id"])["status"] == "unassigned"   # not strict → no re-route
    rep = json.loads((ws / "output" / "advisory_escalation_gate.json").read_text())
    assert rep["strict"] is False and rep["escalated"] == 1 and rep["routed_to_deep_pass"] == 0
