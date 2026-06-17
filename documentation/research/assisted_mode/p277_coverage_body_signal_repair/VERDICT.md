# P277 — VERDICT

## Verdict: **B — BODY_SIGNAL_REPAIR_PROMISING_NEEDS_REFINEMENT**

### Why B (not A)
The body-signal repair **works directionally and safely** — class_routed **39.6% → 41.7% (+2.1pp)**, advisory-only
survivor noise **down 39→35**, **severe FP = 0**, advisory guard PASS, no target-specific/award-text hard-coding, old
behavior preserved when no body is present, all tests green. It even routes a previously-missed EXTERNAL_INTEGRATION
award once the budget constraint is relaxed. So R1 is real and should be kept.

But the gain is **modest**, and the attribution ablation is the decisive reason this is B not A: the **dominant lever is
the poc_budget cap** (budget 5→8 alone = **+11.8pp**, to 51.4%; body adds a further +2.1pp to 53.5%). R1 alone does not
move class_routed to the ≥50% target — the binding constraint was the handoff budget, not classification. Calling R1
"ready for the supervised sweep" (A) would overclaim. Two honest caveats reinforce B:
- a budget-5 round-robin **reshuffle** drops guard classes (ACCESS −6, DOS −4) even as net rises;
- the weakest classes (ORACLE/EXTERNAL) are **recall-bound** (unsurfaced), which R1 cannot fix.

### Not C / D
- Not **C** (NOT_USEFUL): body delivers a real +2.1pp with reduced noise and 0 FP, and routes a missed class at higher
  budget — it is useful, just not sufficient alone.
- Not **D** (ABORTED): research-only, advisory; frozen P260/P262/P264/P267/P269 + configs + P271 + forbidden 5
  byte-identical; only the authorized router/config/tests/p277-files changed; active audit unchanged; 0 FP.

### Recommendation (next, with review)
1. **Keep the body-signal repair** (landed, budget 5).
2. **Land the budget repair next** (poc_budget 5→8, a config knob within hard_max 10) — the dominant lever; backtest
   showed 53.5% routed with body + budget 8, severe FP still 0, EXTERNAL routed, guard classes recovered (DOS 6→7,
   ORDER 2→3). Treat as a distinct, explicitly-approved repair (it widens routing breadth for ALL runs).
3. **Then R2/R3 (recall/manifest)** for the unsurfaced ORACLE/EXTERNAL classes.
4. Re-run the supervised corpus map; if class_routed clears ~50% with severe FP=0, return to a fresh **blind**
   diagnostic target.

Production authority remains **WITHHELD**.
