"""
Task 2 — anti-false-clear checklists. A "reviewed → clean" clear on a permit/erc4626/callback/oracle-
liquidation surface is invalid unless the surface's checklist is completed (Revert Lend false-cleared
H-01 Permit2 + M-14 ERC4626 with no enumerated checks).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
scu = importlib.import_module("spec_checklist_utils")
sweep_write = importlib.import_module("coverage_sweep_write")


# ---------- unit ----------
def test_surface_detection():
    assert "permit" in scu.surfaces_for({"name": "permitTransferFrom", "signature": ""})
    assert "erc4626" in scu.surfaces_for({"name": "redeem", "signature": "function redeem()"})
    assert "callback" in scu.surfaces_for({"name": "onERC721Received", "signature": ""})
    assert scu.surfaces_for({"name": "vegoid", "signature": "function vegoid() view"}) == []


def test_classify_incomplete_and_complete():
    item = {"name": "permitTransferFrom", "signature": "function permitTransferFrom()"}
    inc = scu.classify({"clear_reason": "moves caller's own funds"}, item)
    assert inc["status"] == "incomplete_spec_clear" and inc["surface"] == "permit"
    permit_fields = next(fields for name, _, fields in scu.SURFACES if name == "permit")
    ok = scu.classify({"permit_checklist": {f: "ok" for f in permit_fields}}, item)
    assert ok["status"] == "ok"


def test_new_surfaces_have_distinct_routed_status():
    # reward surface (primary vocab) routes with its own status
    rw = {"name": "notifyRewardAmount", "signature": "function notifyRewardAmount()"}
    assert scu.classify({}, rw)["status"] == "incomplete_reward_accounting_clear"
    # slippage surface (swap is slippage-only primary)
    sw = {"name": "swap", "signature": "function swap()"}
    assert scu.classify({}, sw)["status"] == "incomplete_slippage_deadline_clear"
    # vault->market inflation surface
    s2m = {"name": "supplyToMarket", "signature": "function supplyToMarket()"}
    assert scu.classify({}, s2m)["status"] == "incomplete_vault_market_inflation_deflation_clear"
    assert scu.is_routed("incomplete_reward_accounting_clear")


def test_generic_verb_without_reward_layer_is_fp_safe():
    # a bare _update / transfer in a NON-reward run must NOT pull a reward-accounting checklist
    upd = {"name": "_update", "signature": "function _update(address,address,uint256)"}
    assert scu.classify({"clear_reason": "plain ERC20 bookkeeping"}, upd, {})["status"] == "no_spec_surface"
    # but it does once the run has a reward layer (two-signal gate)
    assert scu.classify({}, upd, {"has_reward_layer": True})["status"] == "incomplete_reward_accounting_clear"


# ---------- integration via coverage_sweep_write ----------
@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "coverage_sweep").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    return tmp_path


def _item(mid, name, score=2):
    return {"id": mid, "kind": "function", "contract": "V3Vault", "file": "V3Vault.sol", "name": name,
            "signature": f"function {name}() external", "in_scope": True, "attack_surface_score": score,
            "tags": [], "source_span": {}}


def _setup(ws, item, decision):
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "source": {}, "items": [item]}))
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps(
        {"dispositions": [{"manifest_id": item["id"], "status": "unassigned"}]}))
    (ws / "data" / "coverage_sweep" / "_decisions.json").write_text(json.dumps({"decisions": [decision]}))


def _run():
    old = sys.argv
    sys.argv = ["coverage_sweep_write"]
    try:
        return sweep_write.main()
    finally:
        sys.argv = old


def _status(ws, mid):
    d = json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]
    return next(x["status"] for x in d if x["manifest_id"] == mid)


def test_permit_clear_without_checklist_routed(ws):
    it = _item("function:V3Vault:pull_permit#1", "pullWithPermit", score=2)
    _setup(ws, it, {"manifest_id": it["id"], "disposition": "cleared", "evidence": ["V3Vault.sol:1"],
                    "reason": "permit moves the caller's own funds, reviewed clean"})
    assert _run() == 0
    assert _status(ws, it["id"]) == "assigned"   # routed to needs_deep_pass (incomplete permit checklist)


def test_permit_clear_with_checklist_clears(ws):
    it = _item("function:V3Vault:pull_permit#1", "pullWithPermit", score=2)
    permit_fields = next(fields for name, _, fields in scu.SURFACES if name == "permit")
    dec = {"manifest_id": it["id"], "disposition": "cleared", "evidence": ["V3Vault.sol:1"],
           "reason": "permit reviewed"}
    # concrete (non-boilerplate) checklist: names the function/line + a yes/no behaviour, so the new
    # adversarial spec-checklist validator accepts it.
    dec.update({f: "pullWithPermit at V3Vault.sol:42 calls permit() then transferFrom(); the received token "
                   "equals the paid token, no extra asset movement occurs" for f in permit_fields})
    _setup(ws, it, dec)
    assert _run() == 0
    assert _status(ws, it["id"]) == "cleared"


def test_plain_getter_untouched(ws):
    it = _item("function:V3Vault:loanCount#1", "loanCount", score=1)
    _setup(ws, it, {"manifest_id": it["id"], "disposition": "cleared", "evidence": ["V3Vault.sol:1"],
                    "reason": "view getter"})
    assert _run() == 0
    assert _status(ws, it["id"]) == "cleared"
