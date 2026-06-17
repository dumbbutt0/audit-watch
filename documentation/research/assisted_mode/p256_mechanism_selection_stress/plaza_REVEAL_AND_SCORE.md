# plaza — Phase 5: Reveal & score

## Freeze integrity (recorded AFTER the three plaza freezes, BEFORE the key was opened)
- `plaza_BASE_FREEZE.md`       sha256 `2359a935bab4b85c…`
- `plaza_MECHANISM_GATE.md`    sha256 `ec5c64c68a4ec626…`
- `plaza_PROCEDURE_OUTPUTS.md` sha256 `a6454e434598d94d…`

## Reveal source
No local key → post-freeze WebSearch/WebFetch of the verified `sherlock-audit/2024-12-plaza-finance-judging`
issues. Awarded findings relevant to the selected loci:

| issue | sev | locus | awarded mechanism |
|---|---|---|---|
| #756 | Med | `Pool` create (collateral level ≤ 1.2) | **non-linear curve below 1.2** ⇒ many small deposits mint more than one large (split-deposit convexity gaming) |
| #714 | Med | `Pool` fee / `claimFees` | **large redeems before `claimFees` reduce collectible fees** (fee computed on the shrunk reserve balance) |
| #761 | High | `Pool` redeem / fee accounting | **pool insolvency**: fees counted globally but not deducted from redemption USD value ⇒ redeemers take more USD value than accounted |
| (auction) | H/M | `Auction.endAuction` / bid | `endAuction` reverts (funds stuck) ; any participant can prematurely end in FAILED_UNDERSOLD and reclaim while locking others |

## Per-locus classification (gate SELECTED/RUNNER-UP vs awarded)
### P-L1 — collateral-level pricing → **ENUMERATED_BUT_RANKED_TOO_LOW** (region-level)
Gate SELECTED **M1 basis asymmetry**; RUNNER_UP **M2 = the ≤1.2 / threshold non-linear branch is exploitable**.
Awarded #756 = exploit of exactly that ≤1.2 non-linear branch (split-deposit convexity). The awarded *region/
branch* was the gate's **runner-up**, ranked below the (non-awarded) basis-asymmetry pick → RANKED_TOO_LOW.
**Honest caveat:** the runner-up named the right branch but a *different specific exploit* (cross-threshold arb vs
split-deposit convexity), so this is region-level RANKED_TOO_LOW, with a partial discovery gap on the exact exploit.

### P-L2 — fee accounting → **ENUMERATED_BUT_RANKED_TOO_LOW** (clean)
Gate SELECTED **M2 repeated-fee-pricing**; RUNNER_UP **M1 = fee priced on moving reserves / `claimFees` collects
less (reconciliation gap)**. Awarded #714 (+#761) is exactly that: large redeems shrink the reserve balance the
fee is computed on ⇒ protocol collects less / insolvency. **The awarded mechanism was the gate's runner-up**,
ranked below the wrong selection → clean RANKED_TOO_LOW.

### P-L3 — auction/coupon → **NOT_ENUMERATED**
Gate mechanisms were poolSaleLimit reserve-drain (selected) + coupon-snapshot drift (runner-up). The awarded
auction bugs are **state-machine**: `endAuction` revert/DoS and premature FAILED_UNDERSOLD termination — neither
was enumerated. Discovery gap on the auction state machine.

## plaza scorecard
| locus | awarded-mechanism class | gate top-2 contained awarded? |
|---|---|---|
| P-L1 | ENUMERATED_BUT_RANKED_TOO_LOW (region) | yes (runner-up, region-level) |
| P-L2 | ENUMERATED_BUT_RANKED_TOO_LOW (clean) | yes (runner-up) |
| P-L3 | NOT_ENUMERATED | no |
| — | RANKED_HIGH_BUT_NOT_COMPLETED | 0 |
| — | COMPLETED_CORRECTLY | **0** |

**Key observations:** (1) the gate **surfaced the awarded mechanism into its top-2 in 2/3 loci** — markedly
better than P255's blind selection (where the awarded mechanism wasn't tracked as a runner-up at all). (2) But in
**both** of those it **ranked the wrong mechanism #1** → 0 selected-and-correct. (3) The 3rd locus was a pure
discovery miss (auction state machine). So the failure splits: **ranking** (P-L2 clean, P-L1 region) +
**discovery** (P-L3, P-L1 exploit-specific). 0 COMPLETED_CORRECTLY.
