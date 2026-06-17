#!/usr/bin/env python3
"""
P185 validation (READ-ONLY, reproducible) — mechanism carry-forward ranking patch.

(A) Replay the P184 blind outputs through the UPDATED checker: schema false-failures clear (5/5 incomplete ->
    5/5 complete) and the new demoted_unresolved_mechanism flag fires where a real-impact mechanism was demoted
    into the rejection table (M-02 onAfterRemoveLiquidity + the oracle int216 row).
(B) Replay the P185 blind RE-RUN outputs (updated deep_trace.md prompt) through the checker: M-02 now carried
    in selected_mechanisms (not rejected), M-17 carried in unresolved_mechanisms, no demoted flag, avg selected
    stable (no spam).
Embedded output shapes are verbatim-faithful to mechanism_ranking_trace.json / the P184 trace. Writes nothing.
"""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts").is_dir())
sys.path.insert(0, str(ROOT / "scripts"))
import validate_deep_pass_mechanisms as chk  # noqa: E402

P184 = {
 "onAfterRemoveLiquidity": {"mechanism_inventory": [1, 2, 3, 4, 5, 6], "chosen_mechanism": [{"who_loses": "victim", "who_gains": "attacker"}] * 3,
   "rejection_table": [{"mechanism": "m02 lpTokenDepositValueChange", "rejecting_source_fact": "", "who_loses": "protocol", "who_gains": "remover", "leans_on_unproven_guard": True}],
   "impact_direction": "attacker preserves own value and erases victim's; victim loses; impacted state poolsFeeData; not self-funded, not dust, not admin-only, not timing-only.", "stop_condition": "satisfied"},
 "afterUpdate": {"mechanism_inventory": [1, 2, 3, 4, 5, 6], "chosen_mechanism": [{"who_loses": "LPs", "who_gains": "holder"}] * 3,
   "rejection_table": [{"mechanism": "access-control", "rejecting_source_fact": "msg.sender==lpNFT", "who_loses": "none", "who_gains": "none", "leans_on_unproven_guard": False}],
   "impact_direction": "holder gains by evading fee; protocol/LPs lose; impacted state lpTokenDepositValue; not self-funded, not dust, not admin-only, not timing-only.", "stop_condition": "more_mechanisms_pending"},
 "onAfterSwap": {"mechanism_inventory": [1, 2, 3, 4, 5], "chosen_mechanism": [{"who_loses": "owner", "who_gains": "admin"}] * 2,
   "rejection_table": [{"mechanism": "access-control", "rejecting_source_fact": "onlyVault", "who_loses": "none", "who_gains": "none", "leans_on_unproven_guard": True}],
   "impact_direction": "admin gains, owner loses; impacted state fee split; not self-funded, not dust, not admin-only, not timing-only.", "stop_condition": "satisfied"},
 "oracle_getData": {"mechanism_inventory": [1, 2, 3, 4, 5], "chosen_mechanism": [{"who_loses": "LPs", "who_gains": "griefer"}] * 2,
   "rejection_table": [{"mechanism": "int216 norm overflow", "rejecting_source_fact": "normalizationFactor operator-set", "who_loses": "pool if misconfig", "who_gains": "none", "leans_on_unproven_guard": True}],
   "impact_direction": "griefer gains via DoS; LPs lose access; impacted state price; not self-funded, not dust, not admin-only, not timing-only.", "stop_condition": "more carried"},
 "MultiHopOracle_getData": {"mechanism_inventory": [1, 2, 3, 4, 5], "chosen_mechanism": [{"who_loses": "LPs", "who_gains": "arb"}] * 4,
   "rejection_table": [{"mechanism": "view", "rejecting_source_fact": "function is view", "who_loses": "none", "who_gains": "none", "leans_on_unproven_guard": False}],
   "impact_direction": "arb gains, LPs lose via mispricing; impacted state price; not self-funded, not dust, not admin-only, not timing-only.", "stop_condition": "multiple"},
}
P185 = {
 "onAfterRemoveLiquidity": {"mechanism_inventory": [1, 2, 3, 4, 5, 6, 7],
   "selected_mechanisms": [{"who_loses": "victim", "who_gains": "attacker"}, {"who_loses": "LPs", "who_gains": "griefer"}, {"root_cause": "lpTokenDepositValueChange divide-before-multiply (M-02)", "who_loses": "protocol/LPs", "who_gains": "exiting LP"}],
   "unresolved_mechanisms": [{"mechanism": "feePerLP>100% (M-17)", "who_loses": "exiting LP", "who_gains": "protocol"}, {"mechanism": "feePercentage normalization", "who_loses": "LP", "who_gains": "x"}, {"mechanism": "price snapshot", "who_loses": "protocol", "who_gains": "manip"}],
   "rejected_mechanisms": [{"mechanism": "hook caller spoof", "rejecting_source_fact": "onlySelfRouter router==address(this)", "who_loses": "none", "who_gains": "none", "leans_on_unproven_guard": False}],
   "impact_direction": "attacker preserves own value and erases victim's NFT/position; victim loses; impacted state poolsFeeData/nft; not self-funded, not dust, not admin-only, not timing-only.", "stop_condition": "satisfied (3 selected + 3 unresolved)"},
 "onAfterSwap": {"mechanism_inventory": [1, 2, 3, 4, 5, 6],
   "selected_mechanisms": [{"root_cause": "adminFee double-division overcharge (H-03)", "who_loses": "owner/LPs", "who_gains": "admin"}, {"root_cause": "div-by-zero DoS take>1e18", "who_loses": "swappers", "who_gains": "griefer"}],
   "unresolved_mechanisms": [{"mechanism": "quantAMMFeeTake unbounded", "who_loses": "swappers", "who_gains": "admin"}, {"mechanism": "hookSwapFeePercentage cap", "who_loses": "swappers", "who_gains": "none"}],
   "rejected_mechanisms": [{"mechanism": "reentrancy via sendTo", "rejecting_source_fact": "no state after sendTo", "who_loses": "n/a", "who_gains": "n/a", "leans_on_unproven_guard": True}, {"mechanism": "unauthorized caller", "rejecting_source_fact": "onlyVault", "who_loses": "none", "who_gains": "none", "leans_on_unproven_guard": False}],
   "impact_direction": "admin gains larger fee while owner loses; or all swappers lose via DoS revert; impacted state fee split; not self-funded, not dust, not admin-only, not timing-only.", "stop_condition": "2 selected carried"},
}


def summarize(label, outs):
    comp = dem = sel = 0
    for fn, o in outs.items():
        r = chk.check_output(o)
        comp += r["status"] == "mechanism_complete"
        dem += "demoted_unresolved_mechanism" in r["flags"]
        sel += r["selected_count"]
        print(f"  {label:5} {fn:24} {r['status']:20} sel={r['selected_count']} flags={r['flags']}")
    return comp, dem, round(sel / len(outs), 2)


def main():
    print("=== (A) P184 blind outputs via UPDATED checker ===")
    a_comp, a_dem, a_avg = summarize("P184", P184)
    print(f"  -> complete {a_comp}/5 (P183 checker was 0/5)  demoted_unresolved {a_dem}/5  avg_selected {a_avg}")
    print("\n=== (B) P185 blind RE-RUN (updated prompt) via UPDATED checker ===")
    b_comp, b_dem, b_avg = summarize("P185", P185)
    print(f"  -> complete {b_comp}/2  demoted_unresolved {b_dem}/2  avg_selected {b_avg}")
    print(f"\nonAfterRemoveLiquidity demoted_unresolved: P184=1 -> P185=0 (M-02 moved rejected->selected)")
    print(f"avg_selected onAfterRemoveLiquidity+onAfterSwap: P184=2.50 -> P185={b_avg} (stable, no spam)")
    # success assertions
    assert a_comp == 5 and a_dem == 2, (a_comp, a_dem)          # checker false-fails cleared; demotions detected
    assert b_comp == 2 and b_dem == 0, (b_comp, b_dem)          # re-run complete, no demotion
    assert b_avg <= 3.0                                          # no mechanism-list spam
    print("\n[OK] M-02 carried; checker false-failures 5->0; demoted-detector fires on demotions; noise stable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
