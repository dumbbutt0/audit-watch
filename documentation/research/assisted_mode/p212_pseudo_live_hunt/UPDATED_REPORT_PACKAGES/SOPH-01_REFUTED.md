# SOPH-01 — withdraw boost conservation  [REFUTED by harness]
- **Outcome:** NOT a finding. Harness shows after full-deposit withdraw `amount == boostAmount` (conservation holds);
  the boost weight is paid (→heldProceeds) and persists by design.
- **Residual observation (Low/Info):** a booster keeps accruing points after withdrawing their deposit (purchased
  weight persists) — possible economic-design note, not a vulnerability. **L3:** FAIL/invalid. Not submission-worthy.
- **PoC:** `forge test --match-contract SOPH01 -vv` (see SOPH01_HARNESS_RESULTS.md).
