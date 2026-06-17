# P257 — Subtle Mechanism Ranking Confirmation + Ablation — SETUP

## Purpose
Confirm the P256 hypothesis (the gate **enumerates the awarded mechanism into the top-2 but ranks the tidier
mechanism #1**) on fully-revealed subtle accounting/state contests, and run a **ranking ablation** (3 profiles)
to learn *which reweighting fixes it*. Five completion ops unchanged. No scaffold, no production edits.

## REVEAL_AVAILABILITY_PRECHECK (new standing target-selection gate; P256 lesson)
Before selecting a target, verify a public report / public findings repo / local sealed key exists and is
retrievable; record the exact source; reject 404 reports / private findings repos / unverified award sources.

### Precheck results (run at planning time)
| target | platform | reveal source | precheck |
|---|---|---|---|
| notional-exponent-2025-06-fresh | Sherlock | `sherlock-audit/2025-06-notional-exponent` (+ judging repo) | **PASS** — repo confirmed; **no award content leaked** by the existence search |
| reserve-2024-07-fresh | Code4rena | `code-423n4/2024-07-reserve-findings` (issue #39 retrievable) | **PASS for retrievability** — BUT the availability search **returned awarded Medium titles** (M-01 DAO-fee distribution, M-02 RSR seizure, M-05 StRSR era, M-06 canceled withdrawal, M-07 traceEnd) |

### Refined precheck rule (P257 lesson)
**Verify reveal *existence* without fetching award *content*.** A content-bearing availability search can return
award summaries and contaminate the blind test — which is exactly what happened to **reserve** here. Use repo/URL
existence checks (HEAD/landing), not "findings High Medium" queries, at selection time.

## Target decision (integrity-driven)
- **notional-exponent — SCORED (clean blind).** No award content was seen; full 7-phase blind run.
- **reserve — EXCLUDED from blind scoring (precheck-contaminated).** Its awarded Medium titles leaked during the
  availability search, so a freeze-before-reveal mechanism-*selection* test on reserve would be hindsight-tainted.
  Recorded for provenance only; contributes **0 scored loci**. (This drops P257 to **n=1 scored contest** — the
  approved "at least 1" floor — and is reported as a limitation.)

Both carry only light p242 Family-A/B "unverified" exposure (those families excluded from selection). Excluded
elsewhere: revert-lend (p189/p191), zaros/silo (p171 answer-key-miss), dyad (p234/p239), all P253–P256 contests,
barred set, P246 reveals.

## The five completion operations (UNCHANGED)
STATE_TRANSITION_SIMULATION (STS) · ADVERSARIAL_ACTOR_SUBSTITUTION (AAS) · TERMINAL_STATE_EVALUATION (TSE) ·
INVARIANT_DELTA_COMPUTATION (IDC) · CROSS_CALL_IDENTITY_TRACKING (CCIT).

## Three ranking profiles (the ablation)
- **Profile A — original P256 gate** (8 dims: controllability/value-delta/victim-gainer/comparand/terminality/
  amplification/simplicity/award-likeness).
- **Profile B — messy-reconciliation weighted** (downweight tidiness/simplicity; upweight reconciliation mismatch,
  insolvency/bad-debt, convexity/nonlinear payoff, delayed accounting drift, state-machine terminality,
  cross-epoch/cross-tx effects, accounting-intent-violated-despite-locally-plausible-math).
- **Profile C — runner-up challenge** (force A's top vs strongest runner-up through 6 adversarial questions;
  runner-up overtakes only with source-backed reasons).

## Method (isolated; no active-audit touch)
Active audit unchanged; checkpoints via `--manifest`/`--out` (invariants re-verified).
- notional checkpoints: accounting 117 recs (AbstractYieldStrategy convert/mint/burn/fees, RewardManager, LPOracle), ST 35.
- reserve checkpoints: accounting 139 (RToken/StRSR/BackingManager/Distributor/Basket), ST 41 — run but UN-SCORED.

## Verdict letters
A RANKING_HARNESS_BUILD_READY · B RANKING_PROMISING_NEEDS_MORE_HELDOUT · C DISCOVERY_GAP_DOMINATES ·
D COMPLETION_GAP_DOMINATES · E RANKING_PROFILES_NOT_USEFUL · F STOP_NOT_USEFUL.
