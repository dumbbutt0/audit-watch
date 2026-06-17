# ethos — Phase 7: Reveal & score

## Freeze integrity (recorded AFTER the six ethos freezes, BEFORE the key was opened)
BASE_FREEZE `9516b8f787333531…` · SELECTED_LOCI `5d097540c0627454…` · MECHANISM_ENUM `38e24048df75ed18…` ·
DISCOVERY_COVERAGE `681eeeb8631c0f2c…` · RANKING_ABLATION `d05b94eacb91305a…` · PROCEDURE_OUTPUTS `3fca75e70aaac5e2…`.

## Reveal source
`code-423n4/2023-02-ethos-findings` + report (post-freeze; **search-level visibility**, not full per-issue).
Awarded findings near my loci:
| issue | locus area | awarded mechanism | family |
|---|---|---|---|
| #693 | `ActivePool._rebalance` | **DoS of liquidations/redemptions by borrowing all AAVE reserves** → yield-vault `withdraw` reverts → `_rebalance` reverts | external-liquidity / state-DoS |
| (theme) | non-18-decimal collateral | decimal-conversion errors across the system | accounting/units |
| (theme) | community issuance → SP | stability-pool issuance accounting | accounting |

## Per-locus scoring (vs my frozen mechanisms/winners)
- **E-L1** (winners: A=E1 profit-recalc, B/C=E2 ERC4626-convexity): awarded #693 = **external-AAVE-liquidity DoS on
  the `_rebalance` withdraw path** → blocks liquidation/redemption. My E2 (share-price convexity) / E3 (rounding) /
  E5 (distribute-before-settle) did **not** include "withdraw can be blocked by external AAVE liquidity." →
  **NOT_ENUMERATED** (the awarded mechanism is an availability/DoS via external dependency I did not enumerate even
  with widening). A/B/C **MISSED_AWARDED**.
- **E-L2** (winners B/C=E2 scale/epoch drift): no clear awarded match to scale/epoch drift in the retrieved set;
  conservatively **NOT_ENUMERATED / unverified** (visibility limit).
- **E-L3** (winners: B=E2 reInsert-C, C=E3 cross-collateral-F): the awarded **non-18-decimal conversion** theme is
  adjacent to my E3 (cross-collateral/decimals) — but it's a decimals-accounting bug, not my identity-binding
  framing → **ENUMERATED_OUTSIDE_TOP5 at best / NOT cleanly SELECTED**. No profile cleanly SELECTED_AWARDED.

## ethos scorecard
| metric | value |
|---|---|
| NOT_ENUMERATED | ~2–3/3 loci (1 adjacent decimals theme, unverified) |
| SELECTED_AWARDED (A/B/C) | 0 / 0 / 0 |
| family that helped | NO_FAMILY_HELPED cleanly (decimals theme partially in family A/E but not selected) |

**Honest note:** the clearest ethos award (#693) is an **external-dependency availability DoS** — a real subtle
bug I missed even with widened enumeration (a genuine discovery failure, not a target-fit excuse). Search-level
reveal limits precise placement of E-L2/E-L3.
