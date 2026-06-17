# P258 — Widened Discovery + Ranking Separation Heldout — SETUP

## Purpose
Separate **discovery failure** from **ranking failure** (and Profile B from C) on subtle accounting/state bugs.
P257 showed the ranking fix works *when the awarded mechanism is enumerated*, but discovery co-dominated. P258
forces **7 mechanism families** into enumeration **before** ranking, then scores whether widened discovery gets
awards into top-2 and whether B/C select them. Five completion ops unchanged; no scaffold; no production edits.

## REVEAL_AVAILABILITY_PRECHECK (existence-only; ran content-safe at planning)
Acceptable: verify report/findings-repo/local-key **exists**. Forbidden pre-reveal: fetching issue/finding titles,
award summaries, severity tables, issue bodies. Leak ⇒ exclude target (reserve, P257).
- **astaria-2023-01** — C4 audit page exists + findings report linked (scope page; **no findings fetched**). **PASS.**
- **ethos-2023-02** — C4 contest repo `code-423n4/2023-02-ethos` confirmed (Liquity-fork + Yearn-V2 vault; README
  scope; **no findings fetched**). **PASS.** Reveal source at scoring: `code-423n4/2023-02-ethos-findings`.
No award content was seen for either pre-freeze.

## Targets (operator-approved astaria + ethos; clean p196-only; multi-family; distinct architectures)
- **astaria-2023-01-fresh** — NFT lending: `PublicVault` (epoch/withdrawReserve/slope), `LienToken` (buyout/debt),
  `AstariaRouter`, auctions. ~375 fns. Families A/C/D/F/G.
- **ethos-reserve-2023-02** — Liquity-fork CDP + Ethos `ActivePool._rebalance` collateral→ERC4626 yield;
  `StabilityPool.offset`, `RedemptionHelper`, `SortedTroves`. ~784 fns (subtle core). Families A/B/C/E/G.
Excluded: all P253–P257 contests; award-revealed (revert-lend/zaros/silo/kelp/ecg/abracadabra/dittoeth/predy);
contaminated (dyad/wildcat/sentiment-v2/fenix/ramses); barred set; P246. Hard locus-exclusion: no math/typo/
mechanical, no missing-revert-only, no single-mechanism loci.

## Source isolation / baseline
Active audit `size-credit-2024-06-blind` unchanged (symlink verified). Checkpoints isolated via `--manifest`/
`--out` into `outputs/` (invariants re-verified). Forbidden baseline (unchanged at end): `c1af70e1`
dashboard_sync · `c095c426` deep_trace · `2a15169a` min_confirm_gate · `afc481c9` confirm_gate · `ae55eb80`
validate_p208. Checkpoint counts: astaria acct 81 / ST 16; ethos acct 71 / ST 42.

## The five completion operations (UNCHANGED)
STATE_TRANSITION_SIMULATION (STS) · ADVERSARIAL_ACTOR_SUBSTITUTION (AAS) · TERMINAL_STATE_EVALUATION (TSE) ·
INVARIANT_DELTA_COMPUTATION (IDC) · CROSS_CALL_IDENTITY_TRACKING (CCIT).

## The 7 discovery families (widened enumeration)
A ACCOUNTING/reconciliation · B CONVEXITY/nonlinear · C STATE_MACHINE/terminal · D REENTRANCY/callback ·
E MIGRATION/upgrade/conversion · F IDENTITY/principal · G TEMPORAL/epoch/checkpoint.

## Three ranking profiles
A original P256 8-dim gate · B messy-reconciliation weighted · C runner-up challenge.

## Scoring vocab
Awarded-mechanism (6): NOT_ENUMERATED · ENUMERATED_OUTSIDE_TOP5 · ENUMERATED_TOP5_BUT_NOT_TOP2 ·
ENUMERATED_TOP2_BUT_RANKED_TOO_LOW · SELECTED_BUT_NOT_COMPLETED · COMPLETED_CORRECTLY.
Per-profile (4): SELECTED_AWARDED · TOP2_AWARDED · MISRANKED_AWARDED · MISSED_AWARDED.
Family-helped (8): ACCOUNTING/CONVEXITY/STATE_MACHINE/REENTRANCY/MIGRATION/IDENTITY/TEMPORAL_HELPED · NO_FAMILY_HELPED.

## Bottleneck (one) & Verdict (one)
Bottleneck: DISCOVERY_GAP_DOMINATES · RANKING_GAP_DOMINATES · COMPLETION_GAP_DOMINATES ·
DISCOVERY_AND_RANKING_BOTH_REQUIRED · PROCEDURE_READY_FOR_HARNESS · PROCEDURE_NOT_USEFUL.
Verdict: BUILD_DISCOVERY_HARNESS · BUILD_RANKING_HARNESS_PROFILE_B · BUILD_RANKING_HARNESS_PROFILE_C ·
BUILD_TOP2_DISCOVERY_PLUS_RANKING_HARNESS · NEEDS_MORE_HELDOUT · STOP_NOT_USEFUL.

## Caveats
Training-confound stands (famous 2023 contests) → credited signal = pre-reveal enumerated+ranked+completed
matching the awarded mechanism; no hindsight; no PoCs.
