"""
Silo Finance forward-looking patch — miss-class routing regression + fixtures + frozen-snapshot replay.

The Silo eval's HIT (M-05 feeShares order) was already converted by the shipped erc4626 `feeshares_order`
field. This patch enforces the surfaces the *misses* mapped onto:
  - M-02 reward-accounting (reward index / totalSupply sync / transfer side-effects)
  - M-04 slippage/deadline (minOut / deadline / user-bounded receipt)
  - M-06 vault->market inflation/deflation (downstream market rounding loss)
plus bridge-lens round 2 (generic vault verbs demoted) and reallocate/flow-cap waiver risk classification.

The enforced regression is disposition-level (drives coverage_sweep_write / bridge_terms / waiver_utils
directly); it never writes into the frozen Silo workspace, and asserts the frozen snapshot is unchanged.
"""
import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
scu = importlib.import_module("spec_checklist_utils")
bt = importlib.import_module("bridge_terms")
wu = importlib.import_module("waiver_utils")
sweep_write = importlib.import_module("coverage_sweep_write")

FIX = ROOT / "tests" / "fixtures" / "silo_miss_class"
AUDIT = ROOT / "audits" / "silo-finance-2025-03-strict-eval"
SNAP = AUDIT / "output" / "pre_answer_key_snapshot"


# ---------------------------------------------------------------- fixtures present
def test_fixtures_present():
    for stem in ("m02_transfer_reward_unsynced_totalsupply", "m04_missing_slippage_deadline",
                 "m06_vault_market_deflation_rounding", "bridge_false_trigger_vault_verbs",
                 "reallocate_flowcap_high_risk_waiver"):
        assert (FIX / f"{stem}.sol").exists(), stem
        assert (FIX / f"{stem}_safe.sol").exists(), f"{stem}_safe"
    assert (FIX / "README.md").exists()


# ---------------------------------------------------------------- unit: new surfaces + context gate
def test_reward_surface_context_gated_fp_control():
    upd = {"name": "_update", "signature": "function _update(address,address,uint256)"}
    # WITHOUT a reward layer in the run, a bare _update is NOT a reward surface (FP control)
    assert scu.classify({"clear_reason": "x"}, upd, {})["status"] == "no_spec_surface"
    # WITH a reward layer, the share-mutation path pulls the reward-accounting checklist
    ctx = {"has_reward_layer": True}
    assert scu.classify({"clear_reason": "x"}, upd, ctx)["status"] == "incomplete_reward_accounting_clear"


def test_slippage_and_inflation_statuses():
    realloc = {"name": "reallocateTo", "signature": "function reallocateTo(address,address,uint256)"}
    assert scu.classify({}, realloc, {})["status"] == "incomplete_slippage_deadline_clear"
    s2m = {"name": "supplyToMarket", "signature": "function supplyToMarket(uint256)"}
    assert scu.classify({}, s2m, {})["status"] == "incomplete_vault_market_inflation_deflation_clear"


def test_build_context_detects_silo_layers():
    items = [{"name": "SiloIncentivesController", "signature": "function _claimRewards()"},
             {"name": "reallocateTo", "signature": "function reallocateTo()"}]
    ctx = scu.build_context(items)
    assert ctx["has_reward_layer"] and ctx["has_external_markets"]


# ---------------------------------------------------------------- bridge lens round 2
def test_generic_vault_verbs_not_bridge():
    assert bt.is_bridge_thread({"title": "deposit and withdraw shares to recipient",
                                "violation_path": ["mint to recipient"]}) is False


def test_generic_verb_plus_crosschain_is_bridge():
    assert bt.is_bridge_thread({"title": "deposit bridged to l2", "violation_path": []}) is True
    assert bt.is_bridge_thread({"title": "withdraw via cross-chain message endpoint",
                                "violation_path": []}) is True


def test_real_bridge_threads_unaffected():
    assert bt.is_bridge_thread({"title": "recipient not validated in escrow release",
                                "violation_path": []}) is True
    assert bt.is_bridge_thread({"title": "cross-chain message handler missing replay guard",
                                "violation_path": []}) is True


# ---------------------------------------------------------------- waiver risk class
def test_reallocate_flowcap_high_risk():
    assert wu.risk_class({"name": "reallocateTo", "signature": "function reallocateTo()"}) == "vault_accounting"
    assert wu.risk_class({"name": "setFlowCaps", "signature": "function setFlowCaps()"}) == "vault_accounting"
    assert wu.risk_class({"name": "setMarketCap", "signature": "function setMarketCap()"}) == "vault_accounting"
    # a genuinely-unrelated view (the safe control) is NOT a high-risk sink
    assert wu.risk_class({"name": "version", "signature": "function version() view returns (string)"}) == "none"


# ---------------------------------------------------------------- integration via coverage_sweep_write
@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "coverage_sweep").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    return tmp_path


def _item(mid, name, score=2):
    return {"id": mid, "kind": "function", "contract": "SiloVault", "file": "SiloVault.sol", "name": name,
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


@pytest.mark.parametrize("surface,name", [
    ("reward_accounting", "notifyRewardAmount"),   # reward primary => has_reward_layer from the item itself
    ("slippage_deadline", "swap"),          # slippage-only primary (swap)
    ("vault_market_inflation_deflation", "supplyToMarket"),
])
def test_new_surface_clear_without_checklist_routed(ws, surface, name):
    it = _item(f"function:SiloVault:{name}#1", name)
    _setup(ws, it, {"manifest_id": it["id"], "disposition": "cleared",
                    "evidence": ["SiloVault.sol:1"], "reason": f"{name} reviewed clean"})
    assert _run() == 0
    assert _status(ws, it["id"]) == "assigned"   # routed to needs_deep_pass (incomplete checklist)


@pytest.mark.parametrize("surface,name", [
    ("reward_accounting", "notifyRewardAmount"),
    ("slippage_deadline", "swap"),
    ("vault_market_inflation_deflation", "supplyToMarket"),
])
def test_new_surface_clear_with_checklist_clears(ws, surface, name):
    it = _item(f"function:SiloVault:{name}#1", name)
    fields = next(f for n, _, f in scu.SURFACES if n == surface)
    # a real strong clear of a value-transfer surface carries BOTH the spec checklist and the special-focus
    # core fields — supply both so the only thing under test is the new spec surface no longer blocking.
    sf_core = {"attacker_entrypoint": "EOA", "cross_function_consumers": "none", "downstream_sinks": "none",
               "state_transition_ordering": "n/a", "value_source_consistency": "consistent"}
    # concrete (non-boilerplate) checklist values — names the function/line, a decision, and accounting vars,
    # so the adversarial spec-checklist validator accepts the clear (boilerplate "verified" would now route).
    concrete = (f"{name} at SiloVault.sol:50 calls _accrueFee()/updateReward before changing _balances; "
                f"rewardIndex and rate include leftover/rollover; does not strand funds or skip accrual")
    dec = {"manifest_id": it["id"], "disposition": "cleared", "evidence": ["SiloVault.sol:1"],
           "reason": f"{name} reviewed", f"{surface}_checklist": {f: concrete for f in fields}, **sf_core}
    _setup(ws, it, dec)
    assert _run() == 0
    assert _status(ws, it["id"]) == "cleared"


# ---------------------------------------------------------------- frozen Silo snapshot untouched
@pytest.mark.skipif(not (SNAP / "_baseline_hashes.txt").exists(),
                    reason="frozen Silo snapshot not present")
def test_frozen_silo_snapshot_unchanged():
    mismatches = []
    for line in (SNAP / "_baseline_hashes.txt").read_text().splitlines():
        if not line.strip():
            continue
        sha, rel = line.split("  ", 1)
        live = AUDIT / rel
        if live.exists() and hashlib.sha256(live.read_bytes()).hexdigest() != sha:
            mismatches.append(rel)
    assert mismatches == [], f"frozen Silo eval mutated: {mismatches}"
