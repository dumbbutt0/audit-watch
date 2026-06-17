# P267 — FAILURE_FORENSICS

Scored prior cases where the awarded mechanism was **visible (enumerated)** but **lost at selection**. Sourced only
from already-scored frozen artifacts (no new answer keys). The recurring shape: a tidier / easier-to-PoC / less
dramatic mechanism is ranked #1 and the higher-terminal-impact awarded mechanism, though present in top-2, is dropped
before completion/PoC.

## Case A — P266 Phi H-03 (the trigger)
- **Selected (wrong):** m1a — `distribute` pays 1% royalty + dust to the arbitrary caller (one-off skim, value-delta
  LOW, easy to PoC: deterministic value flow).
- **Awarded:** m1c — curator-enumeration **gas-DoS** (unremoved zero-balance entries → distribute permanently
  reverts → reward distribution frozen). Permanent, systemic liveness failure.
- **Awarded in top-2?** YES — m1c was in Profile-B top-2 (`RANKING_AND_COMPLETION.md`: "Profile B top-2: [m1a, m1c]").
- **Why wrong won:** m1a was selected as "most PoC-feasible" (a clean deterministic skim) over the harder gas-DoS.
- **What should have flipped it:** terminal-impact dominance (permanent reward-distribution DoS ≫ 1% one-off skim) +
  anti-easy-PoC bias (don't reward m1a *because* it's easier).
- **Would KEEP_BOTH have preserved recovery?** YES — carrying m1c into completion/PoC gives exact recovery a chance.
- **Easier-to-PoC-but-lower-impact?** YES (textbook).

## Case B — P256 Plaza P-L2 (fee accounting)
- **Selected (wrong):** M2 — repeated fee pricing over an un-reset period (systematic worse-pricing; Medium-ish).
- **Awarded:** M1 (the **runner-up**) — reconciliation gap: large redeems shrink the reserve the fee is computed on
  → protocol collects less / **insolvency** (#714 Med + #761 High).
- **Awarded in top-2?** YES — M1 was the gate runner-up (`plaza_REVEAL_AND_SCORE.md`: "the awarded mechanism was the
  gate's runner-up").
- **Why wrong won:** M2 read as the cleaner/more-immediate fee bug.
- **What should have flipped it:** M1's terminal impact (insolvency, a High) dominates M2's systematic-mispricing.
- **KEEP_BOTH preserved?** YES. **Easier-but-lower-impact?** partial (M2 more immediate; M1 higher impact).

## Case C — P256 Plaza P-L1 (collateral-level pricing)
- **Selected (wrong):** M1 — create/redeem basis asymmetry.
- **Awarded:** M2 (the **runner-up**, region-level) — non-linear curve ≤1.2 split-deposit convexity (#756).
- **Awarded in top-2?** YES (runner-up, region-level).
- **What should have flipped it:** the awarded region was the runner-up; KEEP_BOTH preserves it.
- **KEEP_BOTH preserved?** YES (region-level). **Easier-but-lower-impact?** unclear — primarily a ranking miss.

## Case D — P257 Notional N-L2 (fee accrual) — the positive precedent
- **Profile-A pick (tidy, would-be-wrong):** M1 — exp-decay Taylor-approximation error (dust, LOW).
- **Awarded = Profile-B/C pick:** M2 — accrue-timing fee dodge / NAV inconsistency (attacker-controllable entry-path
  ordering; dilutes/dodges fee). `notional_REVEAL_AND_SCORE` confirmed the awarded bug is the messy M2.
- **Awarded in top-2?** YES — B and C both elevated M2; A picked tidy M1.
- **What should have flipped it (and DID under B/C):** attacker control + real value-delta + intent violation
  ("_accrueFees must precede any mint/burn") over M1's bounded dust. This is the precedent the selector formalizes.
- **KEEP_BOTH preserved?** YES. **Easier-but-lower-impact?** YES (M1 tidy/mathy vs M2 messy/higher-impact).

## Case E — P255 BakerFi L5 (harvest) — NOT a selection miss
- **Selected:** P&L-only-when-`deltaDebt==0` mechanism. **Awarded:** flash-loan `fee` not reflected in
  `newDeployedAmount`. `bakerfi_REVEAL_AND_SCORE`: **awarded-mechanism-visible-but-NOT-enumerated** (the fee term was
  never put into the top-2 pair). → This is a **discovery/enumeration** miss, NOT a top-2 ranking miss. A pairwise
  selector that only operates on the enumerated top-2 **cannot** help here → honest **INCONCLUSIVE** for P267.

## Pattern (the thing the selector must fix)
When the awarded mechanism IS in top-2 (A/B/C), it tends to be the **higher-terminal-impact** one (insolvency,
permanent DoS, reward loss, attacker-controllable value redistribution), and it loses to a **tidier / easier-to-PoC /
lower-impact** rival. The fix is a selector that (1) makes **terminal-impact dominance** the primary axis, (2)
applies an explicit **anti-easy-PoC-bias** penalty, and (3) defaults to **KEEP_BOTH** rather than dropping the
high-impact mechanism before PoC. BakerFi shows the selector's honest limit: it cannot recover an awarded mechanism
that was never enumerated.
