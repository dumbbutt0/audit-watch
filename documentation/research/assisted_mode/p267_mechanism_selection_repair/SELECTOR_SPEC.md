# P267 — SELECTOR_SPEC

A deterministic pairwise selector that decides, for two mechanisms already in B/C top-2, whether to SELECT one,
KEEP_BOTH, refute one first, or declare insufficient evidence. Its job is **not** to be perfect — it is to **stop
the higher-terminal-impact awarded mechanism from being dropped before completion/PoC** just because a rival is
easier to PoC. A `KEEP_BOTH` is a success.

## Input (per mechanism, source-derivable, NOT award labels)
| field | enum values | notes |
|---|---|---|
| `impact_class` | permanent_dos · insolvency · stranded_funds · reward_loss · blocked_liquidation_redemption · accounting_corruption · liveness_failure · oracle_misprice · one_off_skim · dust_rounding · local_misprice · griefing_minor | terminal-impact category |
| `value_at_risk` | systemic · multi_user · multi_epoch · single_op · dust | breadth |
| `victim_gainer_clarity` | clear · partial · weak | dimension 3 |
| `intent_violation` | invariant_or_comparand · documented_intent · sibling_parity · none | dimension 4 |
| `attacker_control` | permissionless · conditional · privileged · none | dimension 5 |
| `persistence` | permanent · repeatable · one_off | dimension 6 |
| `refutation_resistance` | survives · conditional · refuted | dimension 7 |
| `poc_feasibility` | easy · moderate · hard | dimension 8 (NEVER a positive selection driver) |

`award_likeness` (dimension 10) is derived from `impact_class` (the award-like classes score high).

## Scores (deterministic, from config weights)
- **terminal_impact_score** = w(impact_class) + w(value_at_risk) + w(persistence). The award-like impact classes
  (permanent_dos / insolvency / stranded_funds / reward_loss / blocked_liquidation_redemption / accounting_corruption
  / liveness_failure) score high; one_off_skim / dust_rounding / local_misprice / griefing_minor score low.
- **validity_score** = w(attacker_control) + w(refutation_resistance) + w(intent_violation) + w(victim_gainer_clarity).
- A mechanism is **plausible** iff `refutation_resistance != refuted` AND `attacker_control != none`.

## Decision rule (deterministic; pair = M1, M2)
Let HI = the mechanism with the strictly higher terminal_impact_score, LO = the other (ties → see below).
1. **Refuted high-impact:** if HI is refuted (`refutation_resistance == refuted`) → `REFUTE_M{hi}_FIRST` (a dramatic
   but refuted mechanism must NOT auto-win — this is the anti-drama guard).
2. **Anti-easy-PoC trap (the P266 fix):** if `terminal_impact(HI) > terminal_impact(LO)` (material gap ≥ `min_gap`)
   AND `poc_feasibility(LO)` is easier than `poc_feasibility(HI)` → set `anti_easy_poc_flag = true`. The outcome is
   then forced to **never SELECT LO**: it is `SELECT_M{hi}` if LO is weak/refuted, else **`KEEP_BOTH`**.
3. **Material impact gap, both plausible:** if gap ≥ `min_gap` and both plausible → `KEEP_BOTH` (protect HI; don't
   drop it for the easier LO).
4. **HI dominates and LO weak:** if gap ≥ `min_gap`, HI plausible, and LO not-plausible (refuted/privileged/none) →
   `SELECT_M{hi}`.
5. **Near-equal impact (gap < `min_gap`):** if exactly one is refuted → `SELECT` the other; elif both plausible →
   `KEEP_BOTH`; else → `INSUFFICIENT_EVIDENCE`.
6. **Fail-closed:** any unresolved/contradictory case → `INSUFFICIENT_EVIDENCE` (never a guessed single winner).

`poc_feasibility` is **never** a positive driver: it can only (a) raise the anti-easy-PoC flag, or (b) act as a
last tiebreaker *toward KEEP_BOTH*. It can never promote a lower-impact mechanism to SELECT.

## Outcomes
`SELECT_M1` · `SELECT_M2` · `KEEP_BOTH` · `REFUTE_M1_FIRST` · `REFUTE_M2_FIRST` · `INSUFFICIENT_EVIDENCE`.
**KEEP_BOTH rule:** both plausible + materially different impact + easier-LO → keep both (never discard HI pre-PoC).

## Advisory contract (every decision, enforced at runtime)
`severity: null` · `reportable: false` · `submission_ready: false` · `concluded: false` · `emits_finding: false` ·
`production_routing: false` · `status: ADVISORY_SELECTOR_DECISION`. Each decision also records: per-mechanism
dimension scores, the decisive dimension(s), the anti_easy_poc_flag, an uncertainty note, and the falsification
questions to resolve before any human escalation. Output bounded (≤ `max_pairs`). A runtime guard raises (exit
nonzero, no decision output) if any decision carries a severity/reportable/submission/concluded/emits_finding/
production_routing value, or a status other than `ADVISORY_SELECTOR_DECISION`, or an unknown outcome. No answer key.
