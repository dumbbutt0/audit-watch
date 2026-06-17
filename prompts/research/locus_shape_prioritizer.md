# Research prompt/spec — Locus-Prioritization + Shape Discovery (P260)

**RESEARCH-ONLY · DEFAULT-OFF · UN-WIRED.** Not a production prompt; not referenced by run_pipeline / agent_policy /
routing / dashboard. Companion to `scripts/research/locus_shape_prioritizer.py`.

## Role in the (research) harness path
`checkpoint-hit locus prioritizer → shape-template application → top-2 mechanism candidates → B/C ranking handoff`

This module is the **upstream locus-selection** step P259 found missing. It does **not** conclude, rank severity,
or submit. It surfaces *which loci to subject to mechanism reasoning* and *which shape templates to apply*, then
hands top-2 mechanism hypotheses to Profile B (messy-reconciliation) / Profile C (runner-up challenge) ranking and
the unchanged five completion operations (STS/AAS/TSE/IDC/CCIT).

## Operator usage
1. Run the isolated checkpoints on the target manifest (accounting + state-transition, default-off, advisory).
2. Run `locus_shape_prioritizer.py --manifest … --accounting … --state-transition … --out …`.
3. For each top prioritized locus, answer the mechanism hypotheses' `falsification_question` + fill the
   `operator-to-derive` fields (attacker action / value delta / victim-gainer / terminality / amplification /
   comparand) — this is the candidate construction the checkpoints alone didn't force at the right locus.
4. Feed `top_2_mechanisms` + `bc_ranking_handoff` to Profile B and Profile C ranking; then five-operation completion.

## Shape templates (T1–T8)
T1 external-dependency-availability · T2 redemption/withdrawal-state-coupling · T3 reentrancy-through-accounting-
boundary · T4 migration/conversion-residue · T5 state-machine-liveness/terminality · T6 cross-transaction-drift ·
T7 liquidation/solvency-boundary · T8 share-price/donation/inflation-boundary.

## Invariants
Emits only interrogative hypotheses (severity:null, concluded:false). Never decides reportability. Requires no
answer key. Known gap: math/units/convergence bug class (e.g. decimals copy-paste, non-convergence) is not modeled
by T1–T8 (candidate future T9). Backtest (P260) is necessary-not-sufficient; live proof is P261 fresh-contest.
