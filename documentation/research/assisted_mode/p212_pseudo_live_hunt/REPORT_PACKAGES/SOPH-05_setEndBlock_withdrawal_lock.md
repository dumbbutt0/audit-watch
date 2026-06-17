# SOPH-05 — setEndBlock(_withdrawalBlocks=0) collapses withdrawal window (admin)
- **Severity recommendation:** Medium (ceiling High; PRIVILEGED → demoted by L3 admin-prereq)
- **Affected:** SophonFarming.sol `setEndBlock` (L287-304), `isWithdrawPeriodEnded`
- **Root cause:** onlyOwner can set `_withdrawalBlocks=0`, making `endBlockForWithdrawals==endBlock`, so the withdraw
  window closes the instant farming ends → users cannot withdraw `depositAmount`.
- **Attacker model:** privileged (owner). **Fund theft:** user funds locked (admin-induced / trust assumption).
- **L3:** high_promotion_allowed=false (attacker_model=privileged) → calibrated Medium. **Mitigation:** enforce a
  minimum withdrawal window. **Human review:** is owner trusted/timelocked? Sherlock admin-input rules apply.
