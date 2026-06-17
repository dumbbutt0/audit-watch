"""
P1/P2 (post-Hybra) — adversarial spec-checklist validation + reward-vocab gap closure + revert exclusion.

Hybra proved the reward_accounting surface routes the right functions but a boilerplate checklist clears them
("reviewed; conserves accounting") → 0 HIT. P1 adds an adversarial validator that rejects confirmatory clears;
P2 closes the vocab gaps (emergencyWithdraw, _claimFees) and excludes unconditional-revert functions.
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
vscc = importlib.import_module("validate_spec_checklist_clears")
sweep_write = importlib.import_module("coverage_sweep_write")

REWARD_FIELDS = next(f for n, _, f in scu.SURFACES if n == "reward_accounting")
RCTX = {"has_reward_layer": True, "has_external_markets": True}


def _reward_clear(value):
    return {"reward_accounting_checklist": {f: value for f in REWARD_FIELDS}}


# ---------- P1: adversarial validator unit ----------
def test_boilerplate_reward_clear_is_confirmatory():
    it = {"name": "notifyRewardAmount", "signature": "function notifyRewardAmount()"}
    for boiler in ("reviewed", "standard", "conserves accounting", "no issue", "safe", "checked",
                   "looks good; works as designed"):
        res = vscc.validate_clear(_reward_clear(boiler), it, RCTX)
        assert res["status"] == vscc.CONFIRMATORY_STATUS, boiler


def test_concrete_reward_clear_passes():
    it = {"name": "notifyRewardAmount", "signature": "function notifyRewardAmount()"}
    concrete = ("notifyRewardAmount at GaugeCL.sol:239 sets rewardRate = rewardAmount/epoch and DOES include "
                "rollover in rewardReserve via syncReward(); leftover is not stranded")
    assert vscc.validate_clear(_reward_clear(concrete), it, RCTX)["status"] == "spec_checklist_valid"


def test_finding_linked_and_known_ref_exempt():
    it = {"name": "notifyRewardAmount", "signature": "function notifyRewardAmount()"}
    d = _reward_clear("reviewed"); d["finding_refs"] = ["X"]
    assert vscc.validate_clear(d, it, RCTX)["status"] == "spec_checklist_valid"
    d2 = _reward_clear("reviewed"); d2["known_ref"] = "blackhole-dup"
    assert vscc.validate_clear(d2, it, RCTX)["status"] == "duplicate_or_known"


@pytest.mark.parametrize("fn", ["receivePenaltyReward", "notifyRewardAmount", "claimRewards", "_createGauge"])
def test_hybra_awarded_functions_blocked_from_superficial_clear(fn):
    """The 4 Hybra functions the reward surface routed must not clear on boilerplate."""
    it = {"name": fn, "signature": f"function {fn}()"}
    # they are reward-surface items …
    assert "reward_accounting" in scu.surfaces_for(it, RCTX)
    # … and a boilerplate checklist is rejected as confirmatory.
    assert vscc.validate_clear(_reward_clear("reviewed; standard; no issue"), it, RCTX)["status"] \
        == vscc.CONFIRMATORY_STATUS


# ---------- P2: vocab gaps + revert exclusion ----------
def test_emergencywithdraw_now_routes_reward():
    it = {"name": "emergencyWithdraw", "signature": "function emergencyWithdraw()"}
    assert scu.classify({}, it, RCTX)["status"] == "incomplete_reward_accounting_clear"
    # FP guard: in a non-reward run (no context) it does NOT route.
    assert scu.classify({}, it, {})["status"] == "no_spec_surface"


def test_claimfees_now_routes_reward():
    for fn in ("_claimFees", "claimFees"):
        it = {"name": fn, "signature": f"function {fn}()"}
        assert scu.classify({}, it, RCTX)["status"] == "incomplete_reward_accounting_clear", fn


def test_unconditional_revert_transfer_excluded():
    body = "function transfer(address,uint256) public override returns (bool) { revert TransfersNotSupported(); }"
    it = {"name": "transfer", "signature": "function transfer(address,uint256)", "source": body}
    assert scu.classify({}, it, RCTX)["status"] == "no_spec_surface"
    assert scu.surfaces_for(it, RCTX) == []
    # flag form
    it2 = {"name": "transferFrom", "signature": "function transferFrom(address,address,uint256)",
           "disabled_revert": True}
    assert scu.classify({}, it2, RCTX)["status"] == "no_spec_surface"


def test_real_transfer_still_routes():
    body = "function transfer(address to,uint256 a) { _balances[to]+=a; rewardIndex++; }"
    it = {"name": "transfer", "signature": "function transfer(address,uint256)", "source": body}
    assert scu.classify({}, it, RCTX)["status"] == "incomplete_reward_accounting_clear"


def test_require_false_body_excluded():
    body = "function approve(address,uint256) public pure returns (bool) { require(false, 'no'); }"
    it = {"name": "approve", "signature": "function approve(address,uint256)", "source": body}
    assert scu.surfaces_for(it, RCTX) == []


# ---------- integration via coverage_sweep_write (strict full-audit) ----------
@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "coverage_sweep").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    return tmp_path


def _item(mid, name, score=2):
    return {"id": mid, "kind": "function", "contract": "GaugeCL", "file": "GaugeCL.sol", "name": name,
            "signature": f"function {name}() external", "in_scope": True, "attack_surface_score": score,
            "tags": [], "source_span": {}}


def _setup(ws, item, decision):
    (ws / "output" / "coverage_manifest.json").write_text(
        json.dumps({"schema_version": 1, "source": {}, "items": [item]}))
    (ws / "output" / "coverage_dispositions.json").write_text(
        json.dumps({"dispositions": [{"manifest_id": item["id"], "status": "unassigned"}]}))
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


def test_integration_boilerplate_routes_concrete_clears(ws):
    it = _item("function:GaugeCL:notifyRewardAmount#1", "notifyRewardAmount", score=2)
    sf = {"attacker_entrypoint": "DISTRIBUTION", "cross_function_consumers": "none", "downstream_sinks": "none",
          "state_transition_ordering": "n/a", "value_source_consistency": "consistent"}
    # boilerplate → routed (assigned)
    dec = {"manifest_id": it["id"], "disposition": "cleared", "evidence": ["GaugeCL.sol:239"],
           "reason": "reviewed", "reward_accounting_checklist": {f: "reviewed; standard; no issue" for f in REWARD_FIELDS}, **sf}
    _setup(ws, it, dec)
    assert _run() == 0
    assert _status(ws, it["id"]) == "assigned"
    # concrete → clears
    concrete = ("notifyRewardAmount at GaugeCL.sol:239 sets rewardRate and DOES include rollover via "
                "syncReward(); leftover not stranded; updateReward runs before stake change")
    dec2 = {"manifest_id": it["id"], "disposition": "cleared", "evidence": ["GaugeCL.sol:239"],
            "reason": "concrete", "reward_accounting_checklist": {f: concrete for f in REWARD_FIELDS}, **sf}
    _setup(ws, it, dec2)
    assert _run() == 0
    assert _status(ws, it["id"]) == "cleared"
