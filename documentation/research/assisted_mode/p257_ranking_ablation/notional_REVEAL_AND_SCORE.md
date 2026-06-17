# notional — Phase 6/7: Reveal & score

## Freeze integrity (recorded AFTER the five notional freezes, BEFORE the judging repo was opened)
- `notional_BASE_FREEZE.md` `7f6ce9fe9c88ca18…` · `notional_SELECTED_LOCI.md` `377e7ed87703c5bc…` ·
  `notional_MECHANISM_ENUM.md` `4fe67b745d31581d…` · `notional_RANKING_ABLATION.md` `93535debae9cdbe4…` ·
  `notional_PROCEDURE_OUTPUTS.md` `6328a06659ab025c…`.

## Reveal source
`sherlock-audit/2025-06-notional-exponent-judging` issues (post-freeze). Relevant awarded findings:
| issue | locus area | awarded mechanism |
|---|---|---|
| **#886** | fee accrual / withdrawal | **Double Fee Accrual in Withdrawal Flow** → last user receives fewer yield tokens (fee counted twice across `_accrueFees` + `feesAccrued()`-in-conversion) |
| #882 | redemption / shares | reentrancy in redemption → break accounting / double-withdraw shares |
| #883 | migration / rewards | users lose latest accrued rewards during migration when `forceClaimAfter > 0` |
| #880 / #879 / #878 | migration / liquidation / sidechain rewards | borrow-calc revert; liquidator slippage; sidechain reward theft |

## Per-locus scoring
### N-L2 fee accrual → awarded **#886** (messy fee double-accrual) — **the clean ablation locus**
My enumeration included the messy fee-timing family (M2 accrue-timing, M3 double-accrual/base-shift) AND the tidy
M1 (Taylor approx error). Profiles:
- **Profile A → M1 (tidy approx)** = **MISRANKED_AWARDED** (the awarded mechanism is the messy double-accrual,
  which A ranked below the tidy pick) → for Profile A the awarded mechanism is **ENUMERATED_BUT_RANKED_TOO_LOW**.
- **Profile B → M2 (messy fee-timing)** = **SELECTED_AWARDED (family-level)** — B's messy-reconciliation
  reweighting elevated the fee-timing/double-accrual mechanism (the #886 family) to #1.
- **Profile C → M2 (messy)** = **SELECTED_AWARDED (family-level)** — runner-up-challenge also overtook the tidy pick.
- Completion: the B/C winner completed to **PARTIAL_CHAIN** pre-reveal → for B/C this is **COMPLETED_CORRECTLY
  (family-level, partial)**; honest caveat: my exact M2 framing was "accrue-timing dodge," the awarded is the
  "double accrual in withdrawal" (M2/M3 same family) — family-level match, not verbatim.

### N-L1 conversion + escrow → **NOT_ENUMERATED**
My N-L1 mechanisms (escrow-excluded-from-supply-not-balance recon; NAV drift; virtual-share) do not match the
awarded escrow/redemption bugs (#882 reentrancy double-withdraw; #883 migration reward loss). The awarded
mechanisms at this area are reentrancy/migration — **not enumerated** in my set. Discovery gap.

### N-L3 escrow + withdraw-request + transient → **NOT_ENUMERATED**
I was in the redemption/withdraw region but enumerated escrow-double-count / withdraw-request-bypass / transient-
stale — **not** the awarded redemption-**reentrancy** (#882). Right region, mechanism not enumerated. Discovery gap.

## notional scorecard (n=3 loci)
| locus | awarded class (Profile A) | Profile A | Profile B | Profile C |
|---|---|---|---|---|
| N-L1 | NOT_ENUMERATED | MISSED | MISSED | MISSED |
| N-L2 | ENUMERATED_BUT_RANKED_TOO_LOW | MISRANKED_AWARDED | **SELECTED_AWARDED** | **SELECTED_AWARDED** |
| N-L3 | NOT_ENUMERATED | MISSED | MISSED | MISSED |

Per-profile awarded selected: **A 0/3 · B 1/3 · C 1/3**. COMPLETED_CORRECTLY (family-level, partial): B 1, C 1, A 0.
Severe FP: 0.

**Per-profile label legend** (the four classes used above): `SELECTED_AWARDED` (profile ranked the awarded
mechanism #1 — N-L2 B/C) · `TOP2_AWARDED` (awarded mechanism in the profile's top-2 but not #1 — none here, since
at N-L2 the awarded mechanism was the runner-up *for Profile A*, captured as MISRANKED_AWARDED) · `MISRANKED_AWARDED`
(awarded mechanism enumerated but ranked below a wrong #1 — N-L2 Profile A) · `MISSED_AWARDED` (awarded mechanism
not enumerated by the profile — N-L1, N-L3 all profiles; shown as MISSED in the table).

## Key observations
1. **The ablation works where the mechanism is enumerated:** at N-L2 the awarded mechanism (#886 messy fee
   double-accrual) was the one **Profile A ranked too low (tidy M1)** and **Profiles B & C selected #1** — a
   direct confirmation of the P256→P257 hypothesis (messy-reconciliation / runner-up-challenge reweighting fixes
   the mis-ranking). **B and C materially outperformed A on this locus (1–0).**
2. **But discovery co-dominates on this contest:** 2/3 awarded mechanisms (#882 reentrancy, #883 migration) were
   **NOT_ENUMERATED** — my accounting-reconciliation loci/mechanisms missed the reentrancy/migration bug shapes.
3. n=3 loci, **1 enumerated** locus → only 1 ranking-ablation data point (clean, but thin).
