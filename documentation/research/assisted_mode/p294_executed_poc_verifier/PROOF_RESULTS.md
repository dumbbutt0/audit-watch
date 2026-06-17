# P294 — PROOF_RESULTS

Real `forge` executions over the proof set (logs under `output/poc_validation/raw/`).

- **awarded loci confirmed by execution: 2** (blackhole-M-04-claim_many, salty-H-increaseUserShare-first-depositor)
- **false hypotheses refused: 1** (salty-Pools-deposit-callback)
- **confirmed false-positive count: 0**
- every confirmation backed by a real passing run + log: **True**

| finding | awarded? | status | attacker_verified | L1/L2/L3 | exploit test → run |
|---|---|---|---|---|---|
| blackhole-M-04-claim_many | True | confirmed_by_execution | True | 111 | test_claim_many_misroutes_to_ownerOf_PASS_SUPPORTED=PASS |
| salty-H-increaseUserShare-first-depositor | True | confirmed_by_execution | True | 111 | test_first_depositor_captures_pool_rewards_PASS_SUPPORTED=PASS |
| salty-Pools-deposit-callback | False | refuted_by_execution | False | 000 | test_callback_reentrancy_is_refuted_PASS_REFUTED=PASS |

## Reading

- **blackhole claim_many** (awarded M-04): the exploit test (`claim_many` misroutes to `ownerOf`) PASSes with a named before/after recipient flip → confirmed_by_execution.
- **salty _increaseUserShare** (P293-recovered): a NET-NEW Tier-C PoC built this phase — first deposit into a pool already holding rewards captures them free (reward-debt snapshot skipped on the zero-supply branch) → confirmed_by_execution. This is the full open-recall→verify loop on a freshly recovered locus.
- **salty Pools.deposit** (false callback hypothesis): only the refutation test passes (no corruption) → refuted_by_execution, attacker_verified=False. The oracle refuses to confirm a non-bug.

confirmed-FP = 0: every confirmation is an awarded locus proven by a real passing exploit run.
