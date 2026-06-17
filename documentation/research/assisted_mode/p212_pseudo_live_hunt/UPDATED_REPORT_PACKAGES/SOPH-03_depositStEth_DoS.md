# SOPH-03 — depositStEth DoS via wrap(full _amount) vs stETH actually received  [CONFIRMED MEDIUM]
- **Severity recommendation:** Medium (executable DoS; L3 FAIL-for-High → calibrated medium; NOT High)
- **Affected:** SophonFarming.sol `depositStEth` (L473-481) → `_depositPredefinedAsset` → `_stEthTOwstEth` → `wstETH.wrap`
- **Root cause:** contract pulls `_amount` stETH but receives `_amount-1/2` (stETH share-rounding); then wraps the full
  `_amount`, which pulls `_amount` stETH from the contract → revert (clean balance) or residual consumption.
- **Attacker model:** permissionless (any stETH depositor); source-valid stETH behavior. **Impact:** DoS of stETH
  deposits; not theft. **Who loses:** stETH depositors (cannot deposit) / protocol (broken entry).
- **PoC:** `cd pocs/p212 && forge test --match-contract SOPH03 -vv`
- **Actual:** with 1-wei rounding `depositStEth(100e18)` reverts. **Control:** honest stETH → succeeds (amount=100e18).
- **Mitigation:** wrap the measured received balance (before/after delta), not the requested `_amount`.
- **Assumptions/limits:** clean-balance case reverts deterministically; with prior residual it consumes residual (still
  an accounting/availability issue). **L3 status:** FAIL-for-High → Medium. **Human review:** confirm stETH path
  in-scope + residual nuance; Medium DoS candidate, human-reviewable.
