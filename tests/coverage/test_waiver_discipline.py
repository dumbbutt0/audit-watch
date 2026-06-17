"""
Task 1 — waiver risk discipline. A high-risk surface (external call, callback, permit, transformer exec,
liquidation, oracle read, vault accounting, access/init) may NOT be waived as a whole cluster (Revert Lend
waived V3Utils.execute that way and lost H-04). It must be waived per-function with a full justification;
those count as recall-risk and are capped.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
wu = importlib.import_module("waiver_utils")
ledger = importlib.import_module("deep_pass_ledger")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    return tmp_path


def _item(mid, name, contract="V3Utils", ext=False, kind="function"):
    return {"id": mid, "kind": kind, "contract": contract, "name": name,
            "signature": f"function {name}() external", "in_scope": True, "external_calls": ext,
            "attack_surface_score": 4, "tags": [], "source_span": {}}


def _setup(ws, items, cluster_id, tier=2, waiver=None):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "source": {}, "items": items}))
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps(
        {"dispositions": [{"manifest_id": i["id"], "status": "assigned", "assigned_pass": "deep"} for i in items]}))
    (ws / "output" / "deep_pass_queue.json").write_text(json.dumps({"clusters": [
        {"cluster_id": cluster_id, "priority_tier": tier, "tier_reason": "special-focus",
         "suggested_specialist": "logic", "item_ids": [i["id"] for i in items]}]}))
    if waiver is not None:
        (ws / "output" / "deep_pass_waiver.json").write_text(json.dumps(waiver))


def _run():
    old = sys.argv
    sys.argv = ["deep_pass_ledger", "--quiet"]
    try:
        return ledger.main()
    finally:
        sys.argv = old


def _summary(ws):
    return json.loads((ws / "output" / "deep_pass_budget_summary.json").read_text())


# ---------- unit: risk classification ----------
def test_risk_class():
    assert wu.risk_class(_item("x", "execute", ext=True)) == "external_call" or wu.risk_class(_item("x", "execute", ext=True)) == "transformer_exec"
    assert wu.risk_class(_item("x", "onERC721Received")) == "callback"
    assert wu.risk_class(_item("x", "permitTransferFrom")) == "permit_signature"
    assert wu.risk_class(_item("x", "liquidate")) == "liquidation"
    assert wu.risk_class({"kind": "constant", "name": "Q96"}) == "none"
    # Silo round 2: reallocation / flow-cap / market-cap sinks are high-risk vault_accounting
    assert wu.risk_class(_item("PublicAllocator", "reallocateTo")) == "vault_accounting"
    assert wu.risk_class(_item("PublicAllocator", "setFlowCaps")) == "vault_accounting"
    assert wu.risk_class(_item("SiloVault", "setMarketCap")) == "vault_accounting"


# ---------- integration: ledger ----------
def test_cluster_waiver_of_high_risk_blocks(ws):
    it = _item("function:V3Utils:execute#1", "execute", ext=True)
    _setup(ws, [it], "DPQ-x-V3Utils", waiver={"waivers": [{"cluster_id": "DPQ-x-V3Utils", "reason": "budget"}]})
    assert _run() == 1
    s = _summary(ws)
    assert any(r["manifest_id"] == it["id"] for r in s["high_risk_waiver_blocked"])


def test_valid_per_sink_waiver_honored_as_recall_risk(ws):
    it = _item("function:V3Utils:execute#1", "execute", ext=True)
    _setup(ws, [it], "DPQ-x-V3Utils", waiver={"waivers": [{
        "manifest_id": it["id"], "function": "execute", "sink": "transformer.call(data)",
        "risk_class": "external_call", "reason": "budget; follow-up",
        "no_impact_justification": "operator-gated; cannot move user funds in this run",
        "answer_independent_reviewer": "lead", "follow_up": "2024-04-01"}]})
    assert _run() == 0   # 1 recall-risk waiver is under the default cap (8) → honored
    s = _summary(ws)
    assert any(r["manifest_id"] == it["id"] for r in s["recall_risk_waivers"])


def test_per_sink_missing_fields_blocks(ws):
    it = _item("function:V3Utils:execute#1", "execute", ext=True)
    _setup(ws, [it], "DPQ-x-V3Utils", waiver={"waivers": [{
        "manifest_id": it["id"], "function": "execute", "sink": "call", "risk_class": "external_call",
        "reason": "budget"}]})   # missing no_impact_justification / reviewer / follow_up
    assert _run() == 1
    s = _summary(ws)
    assert any(r["manifest_id"] == it["id"] for r in s["waiver_requires_per_sink_justification"])


def test_low_risk_cluster_waiver_honored(ws):
    c1 = {"id": "constant:V3Vault:Q96#1", "kind": "constant", "contract": "V3Vault", "name": "Q96",
          "signature": "", "in_scope": True, "attack_surface_score": 3, "tags": [], "source_span": {}}
    _setup(ws, [c1], "DPQ-constants-V3Vault", waiver={"waivers": [{"cluster_id": "DPQ-constants-V3Vault", "reason": "constants only"}]})
    assert _run() == 0
    assert _summary(ws)["high_risk_waiver_blocked"] == []
