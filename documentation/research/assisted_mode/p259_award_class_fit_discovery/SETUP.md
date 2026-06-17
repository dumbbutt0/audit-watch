# P259 — Award-Class-Fit Discovery Confirmation — SETUP

## Purpose
Last diagnostic before build-direction. Remove P258's two confounds — **award-class-fit target screen**
(TARGET_FIT_SCREEN.md) + **full per-issue reveal scoring** — and add **two-pass discovery** to test whether
discovery still fails on fair targets, separating **target-fit / locus / discovery / ranking / completion** gaps.
Five completion ops unchanged; no scaffold; no production edits.

## REVEAL_AVAILABILITY_PRECHECK (existence-only; content-safe)
Allowed: report/findings-repo/local-key existence, metadata, scope, README, source tree. Forbidden pre-reveal:
issue/finding titles, severity tables, award summaries, issue bodies, finding-title-likely searches. Leak ⇒
CONTAMINATED+exclude. **No award content fetched** for hybra; sentiment #541 leaked earlier (P257) → that area
hard-excluded.

## Targets (operator-approved)
- **hybra-finance-2025-10** — SELECT (clean-ish; exclude `RewardsDistributor.claimMany` parity, p161). C4 ve(3,3)+CL.
- **sentiment-v2-2024-08** — disclosed-CONTAMINATED 2nd contest; **#541 (interest-distribution/asset-transfer/fee-
  accrual = `Pool.accrue`) + p242 `max*`/`preview*` HARD-EXCLUDED**; every sentiment result carries an asterisk.
Checkpoint counts: hybra acct 181 / ST 48; sentiment acct 155 / ST 19. Active audit unchanged; checkpoints isolated.

## Five completion operations (UNCHANGED)
STATE_TRANSITION_SIMULATION (STS) · ADVERSARIAL_ACTOR_SUBSTITUTION (AAS) · TERMINAL_STATE_EVALUATION (TSE) ·
INVARIANT_DELTA_COMPUTATION (IDC) · CROSS_CALL_IDENTITY_TRACKING (CCIT).

## Two-pass discovery
- **Pass 1 — 7 families:** A accounting/reconciliation · B convexity/nonlinear · C state-machine/terminal ·
  D reentrancy/callback · E migration/upgrade/conversion · F identity/principal · G temporal/epoch/checkpoint.
- **Pass 2 — 8 shape-generator templates:** (1) external-dependency-availability · (2) redemption/withdrawal
  state-coupling · (3) reentrancy-through-accounting-boundary · (4) migration/conversion-residue ·
  (5) state-machine-liveness/terminality · (6) cross-transaction-drift · (7) liquidation/solvency-boundary ·
  (8) share-price/donation/inflation-boundary.

## Three ranking profiles
A original P256 8-dim gate · B messy-reconciliation weighted · C runner-up challenge.

## Scoring vocab (full per-issue)
In-locus 6 classes: NOT_ENUMERATED · ENUMERATED_OUTSIDE_TOP5 · ENUMERATED_TOP5_BUT_NOT_TOP2 ·
ENUMERATED_TOP2_BUT_RANKED_TOO_LOW · SELECTED_BUT_NOT_COMPLETED · COMPLETED_CORRECTLY.
Outside-locus: OUTSIDE_SELECTED_LOCUS_BASE_MISSED · OUTSIDE_SELECTED_LOCUS_CHECKPOINT_MISSED ·
OUTSIDE_SELECTED_LOCUS_NOT_IN_SCOPE_FOR_THIS_PHASE.
Award-class: subtle_accounting_state · external_dependency_dos · reentrancy_state · migration_conversion ·
mechanical_math_typo · access_control · token_compatibility · other.

## Bottleneck (one) & Verdict (one)
Bottleneck: TARGET_FIT_GAP · LOCUS_SELECTION_GAP · MECHANISM_DISCOVERY_GAP · MECHANISM_RANKING_GAP ·
CHAIN_COMPLETION_GAP · COMBINED_DISCOVERY_PLUS_RANKING_GAP · PROCEDURE_READY_FOR_HARNESS · PROCEDURE_NOT_USEFUL.
Verdict: BUILD_DISCOVERY_HARNESS · BUILD_RANKING_HARNESS_PROFILE_B · BUILD_RANKING_HARNESS_PROFILE_C ·
BUILD_DISCOVERY_PLUS_TOP2_RANKING_HARNESS · NEEDS_MORE_HELDOUT · STOP_NOT_USEFUL. Build threshold: ≥2 scored
contests + ≥2 selected-locus awarded mechanisms (else NEEDS_MORE_HELDOUT/STOP); sentiment is asterisked.

## Caveats
1 clean + 1 contaminated contest; training-confound; full-reveal scoring; no hindsight; no PoCs.
