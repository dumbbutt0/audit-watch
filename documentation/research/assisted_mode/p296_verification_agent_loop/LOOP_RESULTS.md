# P296 — LOOP_RESULTS

- attempted: **3** · new verifier confirmations: **3** · confirmed_FP: **0** · pass: **True**
- new confirmed loci: kelp-2023-11-holdout:H-02, ecg-2023-12-holdout:H-02, ecg-2023-12-holdout:H-03
- confirmed_but_unmapped: none · refuted/setup: none
- not built this wave (next): kelp-2023-11-holdout:M-01, kelp-2023-11-holdout:M-02, ecg-2023-12-holdout:H-01, ecg-2023-12-holdout:M-02, ecg-2023-12-holdout:M-03, salty-2024-01-holdout:H-05
- refutation control (salty-Pools-deposit-callback): refuted_by_execution (attacker_verified=False)

- **cumulative recall-of-confirmed: 6 (P295) + 3 (P296) = 9 loci**

## Per attempted locus (agent_claimed is advisory; verifier is authoritative)

| audit:id | locus | agent_claimed | verifier_verdict | L1L2L3 | assertion_map | clean |
|---|---|---|---|---|---|---|
| kelp-2023-11-holdout:H-02 | LRTDepositPool.depositAsset/getRsETHAmountToMint | confirmed | confirmed_by_execution | 111 | True | True |
| ecg-2023-12-holdout:H-02 | ERC20RebaseDistributor.transfer | confirmed | confirmed_by_execution | 111 | True | True |
| ecg-2023-12-holdout:H-03 | LendingTerm.onBid | confirmed | confirmed_by_execution | 111 | True | True |

## Reading
- 3/3 spawned builders produced faithful Tier-C PoCs the verifier confirmed (ecg onBid bad-debt cascade; ecg rebase-transfer reward theft; kelp deposit-before-calc under-mint) — each with a named L2 flip, an L3 outcome assert, and an assertion_map tying the PASS to the awarded bug.
- confirmed-FP=0: the refutation control stays refuted; every clean confirmation has a real log + assertion_map.
- The loop is reusable: the remaining 6 allowlisted loci + the beanstalk-12 are the next waves.
