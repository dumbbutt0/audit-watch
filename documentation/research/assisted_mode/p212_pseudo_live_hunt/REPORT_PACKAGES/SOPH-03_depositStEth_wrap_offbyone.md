# SOPH-03 — depositStEth wraps full _amount vs actual stETH received
- **Severity recommendation:** Medium (ceiling High; L3 NEEDS_HARNESS, conditional)
- **Affected:** SophonFarming.sol `depositStEth` (L473-481) → `_stEthTOwstEth`
- **Root cause:** stETH `transferFrom(_amount)` can deliver `_amount-1/2` wei (share-rounding); the contract then
  wraps the full `_amount`, which can revert (DoS of deposits) or consume residual stETH (prior users) and credit
  accounting from `_amount` not the real balance received.
- **Attacker model:** permissionless; conditional on stETH rounding. **Fund theft:** conditional residual consumption / DoS.
- **PoC:** NEEDS_HARNESS — faithful stETH mock with 1-wei rounding; assert revert or cross-user residual draw. **L3:** blocked.
- **Mitigation:** wrap the measured received balance (before/after delta), not the requested `_amount`.
- **Human review:** confirm stETH path is in-scope/used; quantify residual-consumption impact.
