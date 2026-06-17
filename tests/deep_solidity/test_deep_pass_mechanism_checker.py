"""P183 — deep-pass mechanism-enumeration advisory checker (no LLM/network)."""
import importlib
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
chk = importlib.import_module("validate_deep_pass_mechanisms")


def _complete():
    return {
        "id": "DT-X", "location": {"function": "onAfterRemoveLiquidity"},
        "mechanism_inventory": ["unauthorized state deletion", "missing invariant enforcement",
                                "victim accounting direction"],
        "rejection_table": [{"mechanism": "missing invariant enforcement",
                             "rejecting_source_fact": "require(sum==ONE) at L42",
                             "why_unexploitable": "bounded", "who_loses": "none", "who_gains": "none",
                             "leans_on_unproven_guard": False}],
        "chosen_mechanism": {"root_cause": "userData-controlled owner", "attacker_model": "EOA",
                             "exploit_path": "...", "who_loses": "LP", "who_gains": "attacker",
                             "why_beats_alternatives": "only one with victim value loss"},
        "impact_direction": {"attacker_receives": True, "attacker_preserves": False, "victim_loses": True,
                             "invariant_violated": True, "not_self_funded_or_dust_or_admin_or_timing": True},
        "stop_condition": "satisfied",
    }


def test_complete_output_passes():
    r = chk.check_output(_complete())
    assert r["status"] == "mechanism_complete" and r["missing"] == []


def test_single_mechanism_output_flagged():
    # the P182 failure shape: one mechanism, no inventory / rejection / impact / stop
    d = {"id": "DT-Y", "location": {"function": "onAfterRemoveLiquidity"},
         "verdict": "MEDIUM_THREAD", "mechanism": "FILO loop underflow"}
    r = chk.check_output(d)
    assert r["status"] == "mechanism_incomplete"
    for f in ("mechanism_inventory", "rejection_table", "impact_direction", "stop_condition"):
        assert f in r["missing"]


def test_inventory_too_short_flagged():
    d = _complete(); d["mechanism_inventory"] = ["only one"]
    assert "mechanism_inventory" in chk.check_output(d)["missing"]


def test_missing_who_loses_gains_flagged():
    d = _complete()
    d["rejection_table"] = [{"mechanism": "x", "rejecting_source_fact": "y"}]  # no who_loses/who_gains
    d["chosen_mechanism"] = {"root_cause": "z"}                                # no who_loses/who_gains
    assert "who_loses_gains" in chk.check_output(d)["missing"]


def test_checker_never_raises_on_garbage():
    for g in ({}, {"mechanism_inventory": None}, {"rejection_table": "x"}, {"impact_direction": 5}):
        assert chk.check_output(g)["status"] == "mechanism_incomplete"


# ---------- P185: list / prose acceptance + demotion detector ----------

def _p185_complete():
    # P185-shaped output: selected_mechanisms as a LIST, impact_direction as structured PROSE
    return {
        "id": "DT-Z", "location": {"function": "afterUpdate"},
        "mechanism_inventory": ["missing invariant enforcement", "wrong lifecycle ordering", "stale snapshot"],
        "rejected_mechanisms": [{"mechanism": "access-control", "rejecting_source_fact": "msg.sender==lpNFT at L577",
                                 "why_unexploitable": "only trusted caller", "who_loses": "none", "who_gains": "none",
                                 "leans_on_unproven_guard": False}],
        "selected_mechanisms": [
            {"root_cause": "no >100 cap on transfer push", "who_loses": "victim", "who_gains": "attacker"},
            {"root_cause": "block.number vs block.timestamp", "who_loses": "protocol", "who_gains": "holder"}],
        "impact_direction": "attacker gains by evading fees; the LP/protocol loses fee value; impacted state is "
                            "lpTokenDepositValue; this is not self-funded, not dust, not admin-only, not timing-only.",
        "stop_condition": "more_mechanisms_pending: distinct state vars",
    }


def test_p185_list_and_prose_accepted():
    r = chk.check_output(_p185_complete())
    assert r["status"] == "mechanism_complete", r["missing"]
    assert r["selected_count"] == 2
    assert "demoted_unresolved_mechanism" not in r["flags"]


def test_p185_demoted_unresolved_flagged():
    # a rejected mechanism WITH real impact whose rejection is unproven -> should have been carried
    d = _p185_complete()
    d["rejected_mechanisms"] = [{"mechanism": "lpTokenDepositValueChange underflow",
                                 "rejecting_source_fact": "", "who_loses": "protocol", "who_gains": "remover",
                                 "leans_on_unproven_guard": True}]
    r = chk.check_output(d)
    assert "demoted_unresolved_mechanism" in r["flags"]


def test_p185_clean_rejection_not_flagged():
    # real source-backed rejection with no impact -> legitimate, no demotion flag
    d = _p185_complete()
    d["rejected_mechanisms"] = [{"mechanism": "reentrancy", "rejecting_source_fact": "nonReentrant at L10",
                                 "why_unexploitable": "guarded", "who_loses": "none", "who_gains": "none",
                                 "leans_on_unproven_guard": False}]
    assert "demoted_unresolved_mechanism" not in chk.check_output(d)["flags"]
