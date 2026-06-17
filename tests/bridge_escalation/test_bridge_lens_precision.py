"""
Task 6 — bridge lens precision. A thread with only L2/oracle/sequencer terms (no bridge coordination term)
is NOT bridge-relevant (Revert Lend T-004 was falsely blocked on a pure 'l2' match). A secondary term paired
with a primary term, or any primary term alone, stays bridge-relevant (no regression on real bridge threads).
"""
import importlib
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
bt = importlib.import_module("bridge_terms")


def _t(title, impact=""):
    return {"title": title, "entry_conditions": "", "attacker_class": "", "impact_estimate": impact,
            "evidence": "", "violation_path": []}


def test_pure_l2_oracle_sequencer_not_bridge():
    # Revert Lend T-004 shape: L2 sequencer / oracle staleness, no coordination term
    assert bt.is_bridge_thread(_t("L2 Chainlink sequencer-uptime check not confirmed",
                                  "stale oracle after sequencer restart")) is False
    assert bt.is_bridge_thread(_t("oracle TWAP manipulation window")) is False


def test_secondary_paired_with_primary_is_bridge():
    assert bt.is_bridge_thread(_t("L2 message replay across the bridge endpoint")) is True
    assert bt.matched_secondary_terms("l2 bridge message") == ["l2"]


def test_pure_bridge_thread_still_bridge():
    assert bt.is_bridge_thread(_t("recipient not validated in escrow release")) is True
    assert bt.is_bridge_thread(_t("cross-chain message handler missing replay guard")) is True
    assert "message" in bt.matched_bridge_terms("cross-chain message handler")


def test_general_oracle_risk_unaffected_token():
    # general oracle/sequencer terms remain in the secondary set (lens untouched), just not bridge-triggering
    assert "oracle" in bt.SECONDARY_L2_ORACLE_TERMS and "sequencer" in bt.SECONDARY_L2_ORACLE_TERMS


# ---- round 2 (Silo): generic vault verbs demoted ----
def test_generic_vault_verbs_alone_not_bridge():
    # Silo non-bridge vault: deposit/withdraw/mint/recipient with NO coordination term → not bridge
    assert bt.is_bridge_thread(_t("deposit and withdraw shares to recipient")) is False
    assert bt.is_bridge_thread(_t("mint vault shares")) is False
    for verb in ("deposit", "withdraw", "mint", "burn", "lock", "recipient", "transfer"):
        assert verb not in bt.PRIMARY_BRIDGE_TERMS
        assert verb in bt.GENERIC_VAULT_VERBS


def test_generic_vault_verb_with_crosschain_context_is_bridge():
    # paired with L1/L2 or a coordination term, the same verb escalates
    assert bt.is_bridge_thread(_t("deposit bridged to l2")) is True
    assert bt.is_bridge_thread(_t("withdraw via cross-chain message endpoint")) is True
