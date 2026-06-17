# P287 — DIAGNOSIS

## Target: kelp-2023-11-holdout (Kelp DAO / rsETH LRT, Code4rena 2023-11) · awarded H/M = 5 (3H/2M)
Fresh, never-scored by the pipeline (`submit_count=0`/`poc_count=0`); selected by content-light H/M screen only.

## Funnel (blind, pre-reveal)
- advisory loci surfaced: 4/5 awarded (80%).
- class routed: 4/5.
- validation queue: 6 candidates.
- READY: 1 (getRsETHAmountToMint).
- PoC-supported: 1.
- **STRONG awarded mechanism recovered pre-reveal: 1 (H-01, Chainlink staleness in the mint valuation).**
- SAME_AREA_WRONG_MECHANISM: 1 (H-02). SUBSYSTEM_ONLY_RECALL: 3 (H-03, M-01, M-02). MISSED outright: 0.
- non-awarded TPs: 0. severe concluded/reportable FP: **0**. false positives: 0.

## First-failed stage for non-recovered awarded findings
- **H-03 (getRSETHPrice donation/first-staker)**: RECALL_GAP — `getRSETHPrice` never surfaced as a candidate (the
  inflation/donation locus wasn't enumerated by the harness on this manifest).
- **H-02 (deposit-before-calc ordering)**: EVIDENCE_DERIVATION_GAP — locus surfaced + READY, but the check-effect
  ordering mechanism (asset transfer before mint calc) is not a deviation the current evidence layer derives (it found
  the oracle-staleness mechanism on the same function instead).
- **M-01 (strategy-update accounting)**: EVIDENCE_DERIVATION_GAP — getTotalAssetDeposits surfaced+queued but stayed
  NEEDS_MORE_EVIDENCE (no source-backed deviation reference).
- **M-02 (slippage control absence)**: EVIDENCE_DERIVATION_GAP — depositAsset surfaced; "missing slippage param" is a
  design-absence the evidence layer doesn't model.

## Comparison to P274 / P286
- P274 (first blind, gondi): 2 EXACT awarded recoveries on a hand-run full path.
- P286 (supervised): READY set → PoC-supported 2/2 on a known target.
- **P287 (fresh blind, frozen stack): 1 STRONG awarded recovery carried surface→route→evidence→READY→PoC-supported,
  pre-reveal, severe FP=0.** The post-repair stack reproduced the end-to-end path on a never-scored target — the
  P284 invariant-delta D4.6 oracle-normalization lens (built on the corpus) fired correctly on fresh code, and P285 D1
  correctly refuted the 4 admin/role-guarded functions. The arc generalized.

## Final bottleneck (exactly one): **I — FULL_PATH_GENERALIZED**
The full path produced a STRONG, PoC-supported awarded recovery on a fresh blind target with FP=0. Residual losses are a
RECALL_GAP (H-03 getRSETHPrice) and EVIDENCE_DERIVATION_GAPs (ordering / strategy-accounting / slippage mechanisms the
current deriver doesn't model) — informative next-repair targets, but not the binding constraint on this run's success.
