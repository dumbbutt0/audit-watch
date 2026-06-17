# P272 — SELECTOR_OUTPUTS (Phase 3)

Frozen **P267** selector (`b0623b8c88752059`) over B/C top-2 pairs from the init-capital advisory candidates.
Dimensions assigned BLIND from source, pre-reveal. Input `p272_selector_input.json` (`89e2f97685a8a35a`); decisions
`p272_selector_decisions.json` (`ce28237c9d676986`); guard PASS.

| pair | M1 (high-impact) vs M2 (easy) | outcome | anti-easy-PoC | gap |
|---|---|---|---|---|
| **L1 liq-incentive** | `getLiqIncentiveMultiplier_e18` min-floor-after-max-cap over-incentive vs edge revert | **KEEP_BOTH** | YES | 3 |
| **L2 health-zero bad-debt** | `liquidate` health==0 → multiplier 0 → unliquidatable / bad debt unrecoverable vs misleading event | **KEEP_BOTH** | YES | 3 |
| **L3 collateral-credit** | `getCollateralCreditCurrent_e36` miscalc → over-borrow/under-liquidation vs rounding dust | **KEEP_BOTH** | YES | 11 |
| Lneg harvest | unsupported/refuted/privileged harvest drama vs benign | **REFUTE_M1_FIRST** | no | 9 |

All three high-impact lending mechanisms preserved (KEEP_BOTH); the unsupported harvest drama correctly
REFUTE_FIRST'd. Frozen before triage.
