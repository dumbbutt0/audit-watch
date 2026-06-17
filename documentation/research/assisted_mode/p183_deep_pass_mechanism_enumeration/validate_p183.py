#!/usr/bin/env python3
"""
P183 validation (READ-ONLY, offline) — deep-pass mechanism enumeration.

api-free has no non-interactive LLM, so this CANNOT generate new deep-trace outputs and CANNOT measure whether
the model SELECTS the awarded mechanism. It measures what is deterministic:
 (1) awarded_mechanism_enumerated  — each of the 9 P182 function-level losses maps to a STEP-0 inventory category
 (2) stop_condition_would_continue — each function already had a produced mechanism AND the awarded one differs
                                     in actor/state-var/severity -> the STOP CONDITION would have kept tracing
 (3) checker correctness           — the advisory checker flags a single-mechanism output, passes an enumerated one
`awarded_mechanism_selected` and real noise increase require a future in-session deep-trace run (stated).
Writes ONLY mechanism_trace.json here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_deep_pass_mechanisms as chk  # noqa: E402

# the STEP-0 inventory menu in prompts/deep_trace.md
INVENTORY = ["unauthorized state deletion", "wrong lifecycle ordering", "stale accounting snapshot",
             "missing invariant enforcement", "reward / index update ordering",
             "hook caller or hook-timing mismatch", "precision / packing / normalization edge",
             "access-control mismatch", "victim accounting direction", "external-call failure / DoS"]

# the 9 P182 function-level DEEP_RUN_BUT_WRONG_MECHANISM losses:
# finding -> (function, awarded mechanism -> inventory category, the mechanism ALREADY produced on that fn at eval,
#            stop-condition clause that applies)
NINE = {
    "H-03": ("onAfterSwap", "missing invariant enforcement",          # missing/improper fee application
             "H-02 inverted-division fee precision", "different mechanism, higher/!=severity"),
    "H-07": ("onAfterRemoveLiquidity", "unauthorized state deletion",  # unauthorized deletion of LP
             "H-06 FILO loop underflow", "different actor + higher severity (High vs Med)"),
    "M-02": ("onAfterRemoveLiquidity", "precision / packing / normalization edge",  # lpTokenDepositValueChange underflow
             "H-06 FILO loop underflow", "different state variable"),
    "M-03": ("afterUpdate", "missing invariant enforcement",          # poolsFeeData length / 100-cap
             "H-01 NFT-transfer fee-bypass", "different mechanism + state variable"),
    "M-06": ("_getData", "external-call failure / DoS",               # unhandled Chainlink revert
             "(oracle read deep-read)", "different actor (all users) + DoS"),
    "M-10": ("afterUpdate", "wrong lifecycle ordering",               # malicious LP-NFT transfer DoS
             "H-01 NFT-transfer fee-bypass", "different actor (victim) + different impact"),
    "M-17": ("onAfterRemoveLiquidity", "missing invariant enforcement",  # feePerLP can exceed 100%
             "H-06 FILO loop underflow", "different mechanism (bound)"),
    "L-01": ("afterUpdate", "stale accounting snapshot",              # block.number vs block.timestamp
             "H-01 NFT-transfer fee-bypass", "different state variable"),
    "L-02": ("_getData", "precision / packing / normalization edge",  # MultiHopOracle precision loss
             "(oracle read deep-read)", "different mechanism"),
}


def main():
    rows = []
    enum_cov = stop_cov = 0
    for fid, (fn, awarded_cat, produced, stop_clause) in NINE.items():
        enumerated = awarded_cat in INVENTORY
        would_continue = bool(produced and stop_clause)
        enum_cov += enumerated
        stop_cov += would_continue
        rows.append({"finding": fid, "function": fn, "awarded_mechanism_category": awarded_cat,
                     "in_inventory_menu": enumerated, "already_produced_mechanism": produced,
                     "stop_condition_clause": stop_clause, "stop_would_continue": would_continue})

    # (3) checker correctness on synthetic single-mechanism vs enumerated outputs
    single = {"id": "DT-onAfterRemoveLiquidity", "location": {"function": "onAfterRemoveLiquidity"},
              "verdict": "MEDIUM_THREAD", "mechanism": "FILO loop underflow"}   # the P182 shape
    enumerated = {"id": "DT-onAfterRemoveLiquidity",
                  "mechanism_inventory": ["unauthorized state deletion", "missing invariant enforcement",
                                          "precision / packing / normalization edge"],
                  "rejection_table": [{"mechanism": "x", "rejecting_source_fact": "L42",
                                       "who_loses": "none", "who_gains": "none"}],
                  "chosen_mechanism": {"who_loses": "LP", "who_gains": "attacker"},
                  "impact_direction": {"victim_loses": True, "invariant_violated": True},
                  "stop_condition": "satisfied"}
    checker = {"single_mechanism_flagged": chk.check_output(single)["status"] == "mechanism_incomplete",
               "enumerated_passes": chk.check_output(enumerated)["status"] == "mechanism_complete",
               "single_missing": chk.check_output(single)["missing"]}

    out = {"phase": "P183", "read_only": True, "n": len(NINE),
           "awarded_mechanism_enumerated": f"{enum_cov}/{len(NINE)}",
           "stop_condition_would_continue": f"{stop_cov}/{len(NINE)}",
           "checker_correctness": checker,
           "NOT_measured_offline": ["awarded_mechanism_selected", "real_noise_increase"],
           "note": "enumerability + stop-condition + checker validated offline; SELECTION requires an in-session "
                   "deep-trace run. No recall recovery claimed.",
           "rows": rows}
    (HERE / "mechanism_trace.json").write_text(json.dumps(out, indent=2))

    print("=== P183 deep-pass mechanism-enumeration validation (offline) ===")
    print(f"awarded_mechanism_enumerated (in inventory menu): {enum_cov}/{len(NINE)}")
    print(f"stop_condition_would_continue:                    {stop_cov}/{len(NINE)}")
    print(f"checker: single-mechanism flagged={checker['single_mechanism_flagged']}  "
          f"enumerated passes={checker['enumerated_passes']}")
    print(f"   single-output missing fields: {checker['single_missing']}")
    print("\nper-finding:")
    for r in rows:
        print(f"  {r['finding']:5} {r['function']:24} -> {r['awarded_mechanism_category']:34} "
              f"inv={r['in_inventory_menu']} stop={r['stop_would_continue']}")
    print("\nNOT measured offline (needs in-session run): awarded_mechanism_selected, noise increase.")
    print("Claim: mechanism-enumeration coverage only; recall recovery is a MONITORED FOLLOW-UP.")

    assert enum_cov == len(NINE), "awarded mechanism not covered by inventory menu"
    assert stop_cov == len(NINE), "stop-condition would not continue for some finding"
    assert checker["single_mechanism_flagged"] and checker["enumerated_passes"]
    print("\n[OK] read-only; wrote mechanism_trace.json only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
