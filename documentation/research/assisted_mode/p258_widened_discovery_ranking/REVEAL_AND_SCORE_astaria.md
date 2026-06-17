# astaria — Phase 7: Reveal & score

## Freeze integrity (recorded AFTER the six astaria freezes, BEFORE the key was opened)
BASE_FREEZE `24827d902c44ea87…` · SELECTED_LOCI `435ce0d285f99671…` · MECHANISM_ENUM `416b91680df93031…` ·
DISCOVERY_COVERAGE `a7d6eb5a7697facd…` · RANKING_ABLATION `bc689dc2de3b3f8c…` · PROCEDURE_OUTPUTS `b72c5a5c8458e29f…`.

## Reveal source
`code-423n4/2023-01-astaria-findings` + report (post-freeze; **search-level visibility**, not full per-issue).
Awarded findings near my loci:
| issue | locus area | awarded mechanism | family |
|---|---|---|---|
| #54 | `transferWithdrawReserve` | ERC20 0-amount-transfer revert blocks the function (DoS) | mechanical/token-compat |
| (—) | `transferWithdrawReserve` | **no access control** | access-control |
| #254/#424 | `PublicVault` ERC4626 | fee-on-transfer tokens lock funds | token-compat |
| #375 | liquidation | `liquidationInitialAsk` cast to uint88 → collateral locked | casting |
| (refi) | refinance/liquidation | permissionless refinance sets low `liquidationInitialAsk` → cheap liquidation | griefing |
| #112 | auction/ClearingHouse | dust transfer settles auction | auction-griefing |

## Per-locus scoring (vs my frozen mechanisms/winners)
- **A-L1** (winners: A=A4 slope-G, B/C=A2 epoch-C): awarded = transferWithdrawReserve **access-control** + 0-transfer
  **DoS** (#54) → **NOT_ENUMERATED** (my subtle epoch/slope/reentrancy mechanisms were not the awarded
  access-control/token-compat ones). All profiles **MISSED_AWARDED**.
- **A-L2** (winners: A=A1 interest, B=A2 stale-accrual, C=A3 payee-F): awarded = liquidationInitialAsk uint88 cast
  (#375) + refinance-low-ask griefing → **NOT_ENUMERATED** (my buyout accrual/identity mechanisms ≠ the awarded
  cast/refinance-ask). MISSED_AWARDED all profiles.
- **A-L3** (winners: A=A1 rounding, B/C=A2 future-epoch): awarded near redeem = fee-on-transfer (#424) → **NOT_ENUMERATED**.

## astaria scorecard
| metric | value |
|---|---|
| awarded mechanisms in my selected loci | mechanical/access-control/casting/griefing/token-compat |
| NOT_ENUMERATED | 3/3 loci |
| ENUMERATED_TOP2_BUT_RANKED_TOO_LOW | 0 |
| SELECTED_AWARDED (A/B/C) | 0 / 0 / 0 |
| family that helped | **NO_FAMILY_HELPED** (awards fall in the mechanical/access-control class the phase excluded by design) |

**Honest note:** astaria's awarded set skews **mechanical / token-compat / access-control / casting** — i.e. the
bug-class P258 deliberately excluded. So "NOT_ENUMERATED" here partly reflects **target-fit** (astaria's awards
aren't the subtle-accounting class), not pure discovery failure. The existence precheck verified retrievability
but **not award-class fit** — a new target-selection lesson.
