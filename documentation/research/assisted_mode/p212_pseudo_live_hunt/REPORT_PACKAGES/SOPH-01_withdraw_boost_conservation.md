# SOPH-01 — withdraw() omits boostAmount decrement (conservation break)
- **Severity recommendation:** Medium (threat ceiling High; L3 NEEDS_HARNESS → NOT High-ready)
- **Affected:** SophonFarming.sol `withdraw` (L699-742); state UserInfo/PoolInfo.boostAmount
- **Root cause:** withdraw decrements `user.amount`/`pool.amount` by `_withdrawAmount` (the deposit slice) but never
  decrements `user.boostAmount`/`pool.boostAmount`, so the invariant `amount == depositAmount + boostAmount-derived`
  diverges; reward (points) weight continues to accrue on phantom boost the user no longer effectively holds.
- **Attacker model:** any depositor (permissionless). **Who loses/gains:** honest depositors lose relative point share;
  withdrawer retains inflated weight. **Fund theft:** none (withdraw bounded by depositAmount).
- **Exploit steps:** deposit with boost; withdraw deposit slice; observe boostAmount unchanged + continued pending accrual.
- **PoC:** NEEDS_HARNESS (not built). **Actual/expected:** to be measured by a forge harness (deploy proxy+pool+mock LST).
- **Mitigation:** decrement boostAmount proportionally on withdraw (or recompute amount from deposit+boost).
- **Assumptions/limits:** points→L2 allocation materiality unproven without harness. **L3:** blocked_by_missing_l3_poc.
- **Human review:** confirm whether phantom weight materially drains others' allocation; build harness; then re-grade.
