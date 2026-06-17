# P292 — REMAP_RESULTS

8 audits (salty/ECG/kelp/blackhole/panoptic/silo/revert-lend/hybra). Sources: `outputs/remap_metrics.json`,
`outputs/duplicate_class_decisions.json`, `outputs/internal_locus_admission_report.json`.

## Admission (the repair)
- **Internal-locus exceptions admitted: 3** — `salty StakingRewards._increaseUserShare` (the P291-blocked awarded H-02/
  H-04 locus), `ECG ERC20RebaseDistributor.updateTotalRebasingShares`, `silo SiloVault._convertToSharesWithTotalsSafe`.
  All distinct, class-relevant (SHARE/REWARDS), reached from public entries.
- queue size: salty 10→11, ECG →9, silo →11 (bounded +1 each); others unchanged. Monoculture OK on all 8 (max class
  fraction ≤0.27). Bounded (≤1 admitted/audit ≤ caps 2/class,5/contest).
- duplicate_class_decisions: ADMITTED_INTERNAL_LOCUS_EXCEPTION 3 · DEFERRED_DUPLICATE_CLASS (rest) · 0
  DEFERRED_INTERNAL_LOCUS_CAP · 0 DEFERRED_MONOCULTURE_GUARD.

## Reaches Lens 3? — YES; Lens 3 lift? — NO (precise block)
All 3 admitted internal loci now REACH the deriver/gate/Lens 3. Each gets **NEEDS_VALUE_FLOW_EVIDENCE** with
invariant_delta `NO_REFERENCE` — Lens 3 (reward_index_init) RECEIVES the candidate but does not fire, because the
reward-index logic is not span-local-visible (e.g. `_increaseUserShare` has share/stake terms but no in-span
rewardIndex/userIndex/claim terms — the index accounting lives in a callee / uses non-standard naming). A precise
non-READY block, not a silent miss. **0 false READY.**

## Regressions (all stable; via frozen evidence_packages)
ECG H-04 stake READY · kelp H-01 getRsETHAmountToMint READY · blackhole claim_many READY · L2Governor.execute READY ·
salty Pools.deposit NEEDS_INTEGRATION_DEVIATION_EVIDENCE (P291 precision held). **severe concluded/reportable FP = 0**
across all 8 audits. No new READY anywhere.
