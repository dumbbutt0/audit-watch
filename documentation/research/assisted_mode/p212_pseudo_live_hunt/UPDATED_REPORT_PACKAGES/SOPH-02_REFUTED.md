# SOPH-02 — accPointsPerShare scaling  [REFUTED by harness]
- **Outcome:** NOT a finding. `pendingPoints` view == post-`updatePool` settled (delta 0 for both users); the
  `*1e18 … /1e36` scaling cancels correctly. No 1e18 over-report.
- **Residual (Low/Info):** integer truncation dust in `pointReward/lpSupply` (bounded). **L3:** FAIL/invalid.
- **PoC:** `forge test --match-contract SOPH02 -vv` (see SOPH02_HARNESS_RESULTS.md).
