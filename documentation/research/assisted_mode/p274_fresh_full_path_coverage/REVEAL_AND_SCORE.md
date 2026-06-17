# P274 — REVEAL_AND_SCORE (Phase 10)

Answer key opened **after** the Phase-9 pre-reveal set was frozen + hashed. Source: `code-423n4/2024-04-gondi-findings`
(`report.md`; 17 High, 20 Medium awarded). Scoring is against the frozen set only; no hindsight credit.

## Headline — TWO EXACT awarded-High recoveries pre-reveal, both with passing runtime PoCs

### M1 → **H-03 (High, Access Control)** — EXACT
Award: *"Function `distribute()` lacks access control allowing anyone to spam and disrupt the pool's accounting."*
My pre-reveal M1 (frozen `POC_INTENT`/`POC_RESULTS`): *"`distribute()` is permissionless and forwards
caller-supplied tranche data into the trusted `loanLiquidation` callback on a registered LoanManager — no auth, no
loan-existence check → corrupts pool accounting."* Same **root cause**, same **locus** (`distribute` →
`_handleLoanManagerCall` → `loanLiquidation`), same **fix** ("only allow Loan contracts to call distribute").
PoC `test_permissionless_spoofed_liquidation_callback` PASS: EOA reaches `loanLiquidation` with attacker-controlled
`loanId`/`principal`. Negative control PASS (split math conserves → isolates the bug to the missing auth).
- Match level: **EXACT** (root cause + locus + fix). PoC proves L1 entry / L2 attacker-param control / L3 callback
  reached. Economic write-off in a *real* Pool not executed → recorded **partial on economic magnitude, exact on
  mechanism**. The award's `principalAddress`-not-validated detail is one instantiation of the same root cause.

### M2 → **H-02 (High, Math)** — EXACT
Award: *"Division before multiplication could lead to users losing 50% in `WithdrawalQueue`"* in `_getAvailable` /
`_getWithdrawablePerShare`. My pre-reveal M2: *"`_getWithdrawablePerShare` divides by `getTotalShares` before
multiplying by a position's shares → remainder permanently stranded; `getTotalShares==0` reverts."* Same **mechanism**
(division-before-multiplication), same **locus**, same **fix** (multiply before divide).
PoC `test_per_share_rounding_strands_funds` PASS (stranded = `funded % totalShares`) + `test_div_by_zero_before_first_mint`
PASS.
- Match level: **EXACT** (mechanism + locus + fix). I under-characterized the *magnitude* (framed as dust; the award
  shows ~50% with adversarial share counts) but the mechanism is identical.

## The other candidates (honest)
| candidate | award? | classification |
|---|---|---|
| M3 `burnAndWithdraw` strands unlisted assets (proven) | QA-Low `[03]` is the *old-ERC721* variant; my exact mechanism (caller-omitted asset) differs | **NON-AWARDED TRUE POSITIVE** (real, same function, QA-adjacent area) |
| M4 `offers` order validation | **H-13** = missing `executionData.duration ≤ offer.duration` in this exact locus | **SUBSYSTEM_ONLY / SAME_AREA** — locus surfaced + examined, exact mechanism missed (I logged NEEDS_MORE_RUNTIME) |

## Award-class loci that recall surfaced but the path did not convert
- `settleWithBuyout` (**H-05 triggerFee theft**, **H-06 missing `loanLiquidation`**) — routed to STATE class but lost
  the within-class tiebreak to `burnAndWithdraw`; examined in completion, not PoC'd → **SUBSYSTEM_ONLY**.
- `mergeTranches` (**H-01** accounting, **H-14** missing `nonReentrant`) — surfaced, DEFER_DUPLICATE_CLASS (DOS) →
  **SUBSYSTEM_ONLY**.
- queue accounting (**H-07/H-08/H-09**) — adjacent loci (`deployWithdrawalQueue`, `_queueClaimAll`, WithdrawalQueue)
  surfaced, exact mechanisms not pursued.

## False positives
**0 severe concluded/reportable FP.** No candidate was concluded as a vulnerability that the reveal refutes; the one
negative control behaved as predicted (split conserves). M3/M4 are real (TP / same-area), not FPs.

## Coverage scorecard (the P272 mismatch test)
- Routed classes: ORDER, SHARE, DOS, ACCOUNTING, STATE (5).
- **The two EXACT recoveries came from TWO DISTINCT award classes** — **ACCESS_CONTROL** (H-03 via the
  ACCOUNTING-routed `distribute`, mechanism is access-control) and **MATH/SHARE** (H-02 via the SHARE-routed
  WithdrawalQueue). The P272 accounting-monoculture would have spent all slots on accounting and missed both; the
  coverage layer prevented that.
