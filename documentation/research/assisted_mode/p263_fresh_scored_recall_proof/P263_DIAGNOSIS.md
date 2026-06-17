# P263 — DIAGNOSIS
- Scored contest: 1 (benddao, public findings). Awarded: 8 High + 20 Medium (full per-issue reviewed).
- Subtle-accounting/state Highs: ~4 (H-01,H-05,H-06,H-08); the other Highs are access_control (H-02,H-03,H-07) /
  mechanical (H-04) = out of the recall-first target class.
- **Narrow baseline (top-5) vs recall sweep:** narrow = 100% liquidation/interest/deposit, ZERO yield loci. Sweep
  forced 17 loci, 12 recall-delta — INCLUDING the yield-staking subsystem (H-01/H-06/H-08 Highs) and bad-debt/
  liquidation (H-05, GenericLogic, T7). => recall sweep surfaced an **award-dense subsystem (3 Highs) the narrow
  path skipped**.
- Awarded loci forced by recall sweep (outside narrow top-5): yield-staking (H-01/H-06/H-08 + M-06/07/15/16),
  GenericLogic bad-debt (H-05), cross/isolate-liquidation deltas (M-14). 
- Selected → completed: SL1 (yield unstake/repay) → T5 liveness PARTIAL_CHAIN **family-matching H-08** (forced-in,
  outside narrow). SL3 → T7 family-matches M-13 (area). SL2/SL4 no clean recovery.
- FP: 0 severe concluded/reportable (sweep advisory; manual only PARTIAL hypotheses).
- **Did recall-first improve scored recall over narrow selection?** YES on LOCUS-RECALL: the yield-staking award
  subsystem (3 Highs) is recovered into discovery only because the sweep ran shape discovery before narrow selection.
- Remaining gap: MECHANISM-PRECISION + COMPLETION — matches are family-level (T5≈H-08, T7≈M-13), not exact root-
  cause or verified exploit; downstream ranking/completion must do the precision work.

## Bottleneck status
PROCEDURE_WORKING for LOCUS-RECALL (the P259 leak the harness targets). Residual = mechanism-precision/completion
(downstream), + training-confound (benddao well-known) + n=1 scored contest.
