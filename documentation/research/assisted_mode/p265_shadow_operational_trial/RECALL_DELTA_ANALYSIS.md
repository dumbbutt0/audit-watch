# P265 — RECALL_DELTA_ANALYSIS (metric #8, the core signal)

Recall-delta = advisory candidates the **narrow top-5 baseline would skip** (P260 rank ≥5 or rank `null`, forced in
by a recall-first clause). This is deterministic from the outputs (no award knowledge), so it is valid across all 13.

## Pooled
- **157 / 216 = 72.7%** of advisory candidates are recall-delta. narrow baseline = 59.
- Per-contest recall-delta fraction ranges 0.55 (loopfi 8/13) → 0.78 (reserve 18/23, hybra 18/23).
- **Interpretation:** the harness is overwhelmingly a *discovery-widening* engine. Roughly 3 of every 4 candidates
  it surfaces are loci the pre-P262 narrow path never would have examined. The narrow top-5 alone reproduces only
  the obvious liquidation/interest/deposit core; the recall-first clauses are what reach the subtle subsystems.

## The benddao clean-anchor proof (decisive, reproduced here)
The shadow run reproduces P263's decisive fact exactly. Narrow top-5 = {`_repayUserERC20Debt`,
`executeCrossLiquidateERC721`, `calculateUserAccountDataForLiquidate`, `updateInterestIndexs`,
`validateDepositERC721`} — **100% liquidation/interest/deposit; zero yield-staking.** The recall-first sweep forces
in the **entire yield-staking subsystem** as recall-delta:
`YieldStakingBase.batchStake` (rank6, T5) · `batchUnstake` (rank10, T2/T5) · `batchRepay` (rank11, T5) ·
`_unstake` (rank15, T2) · `YieldSavingsDai.batchUnstakeAndRepay` (rank16, T2/T5) — plus
`GenericLogic.calculateUserAccountData` (rank12, T7) = the H-05 bad-debt insolvency locus.

Awarded coverage (benddao, public): the yield subsystem carries Highs **H-01 / H-06 / H-08** + Mediums M-06/07/15/16,
and H-05 (bad-debt) sits on `calculateUserAccountData`. **All of these are recall-delta** — zero-represented in the
narrow top-5, forced in by the sweep. The 4 out-of-class Highs (H-02/H-03/H-07 access-control, H-04 math) are
correctly silent (the accounting/state checkpoints don't target those families).

## What recall-delta does NOT prove
- It proves the award-carrying **locus** is surfaced, not that the **mechanism** is constructed. benddao H-08 only
  reached a **family-level T5 PARTIAL** (P263 manual completion); exact-mechanism = 0. Locus recall ≠ exact recovery.
- Across the contaminated retrospective set the same split holds: loci forced in (hybra `GrowthHYBR.deposit`,
  sentiment bad-debt T8, ethos `_rebalance` T1, plaza fee T-runner-up) but mechanism either mis-ranked (plaza,
  notional Profile A), family-level (benddao H-08), or refuted/wrong (bakerfi harvest). The recall layer is the
  layer that works; the **completion/exact-mechanism layer is the open gap (P266)**.
