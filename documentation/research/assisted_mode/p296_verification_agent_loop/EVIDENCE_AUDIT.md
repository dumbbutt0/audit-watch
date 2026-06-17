# P296 — EVIDENCE_AUDIT

## Each new confirmation = a real forge exploit PASS (L1+L2+L3) + assertion_map mapping it to the awarded bug
| audit:id | locus | exploit test (real PASS) | L2 named flip | L3 outcome | maps to bug |
|---|---|---|---|---|---|
| ecg H-03 | LendingTerm.onBid | test_onBid_loss_cascades_to_unrelated_lender_PASS_SUPPORTED | creditMultiplier 1e18→0.95e18; B value 1000e18→~950e18 | assertLt(bValueAfter,bValueBefore) | onBid forwards pnl<0 to notifyPnL → global creditMultiplier decremented → unrelated lender B loses 5% (bad-debt cascade, not access) |
| ecg H-02 | ERC20RebaseDistributor.transfer | test_rebase_reward_theft_via_transfer_PASS_SUPPORTED | Alice/Bob rebased balances before/after a mid-interpolation transfer | assertEq(stolen,50e18) | a mid-distribution transfer concentrates the sender's unminted reward stream onto the recipient → Alice 400e18 vs fair 350e18 |
| kelp H-02 | LRTDepositPool.depositAsset | test_deposit_before_calc_undermints_PASS_SUPPORTED | pool balance 100e18→200e18, in-mint price 1.0→2.0 | assertLt(mintedActual 50e18, mintedExpected 100e18) | transferFrom runs before getRsETHAmountToMint → inflated balance → depositor under-minted by 50e18 |

For each, the verifier (`executed_poc_verifier`) re-ran forge and required [PASS] of the named exploit test + L1
(attacker prank) + L2 (named flip) + L3 (outcome assert), backed by a captured log under output/poc_validation/raw/.
The manifest assertion_map's `proves` field ties the assertion to the awarded mechanism (audited above).

## Faithfulness (Tier-C)
Each subagent copied the bug-locus control-flow VERBATIM (onBid pnl→notifyPnL global-multiplier branch;
distribute/transfer/_burn/updateTotalRebasingShares interpolation; depositAsset→getRsETHAmountToMint→getRSETHPrice
ordering) and mocked only the irrelevant bookkeeping. forge-std only, no fork. Contest source untouched (PoCs under
pocs/p296/ only).

## Verifier-authoritative (judge ≠ builder)
All 3 builders self-reported "confirmed" and the verifier independently agreed (clean=True). The override path — a
builder claiming confirmed on a FAILING exploit → verifier attacker_verified=False — is proven by the synthetic test
`test_builder_claim_ignored_when_exploit_fails`. The assertion_map gate (verifier-PASS without a map = not clean) is
proven by `test_pass_without_assertion_map_is_unmapped`.

## No confirmed false positive
confirmed_false_positive_count = 0. The salty Pools.deposit refutation control stays refuted_by_execution. Every
clean confirmation has a real passing log AND an assertion_map (guard_report `every_clean_confirmation_has_log_and_map`).
