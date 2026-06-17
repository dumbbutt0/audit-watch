# P269 — TRIAGE_POLICY_SPEC

Deterministic impact-first triage that ranks advisory candidates for the PoC path so award-class-fit subsystems are
routed (heavy if needed) instead of de-scoped for the easiest PoC. Advisory only.

## Input (per candidate; source-derivable, NOT award labels)
| field | values | notes |
|---|---|---|
| `id` / `locus` / `subsystem` | str | subsystem groups clustering (e.g. "native_vault_slashing_snapshot") |
| `impact_class` | slashing · bad_debt · insolvency · liq_redemption_blockage · permanent_reward_loss · snapshot_checkpoint_corruption · statemachine_terminal_failure · cross_domain_accounting_mismatch · systemic_liveness_failure · one_off_skim · dust_rounding · local_misprice · griefing_minor | top group = award-class-fit |
| `recall_delta` | bool | surfaced beyond narrow baseline |
| `terminality` | permanent · repeatable · one_off | |
| `value_at_risk` | systemic · multi_user · single_op · dust | |
| `selector_outcome` | SELECT_M1/M2 · KEEP_BOTH · REFUTE_*_FIRST · INSUFFICIENT (or null) | P267 output |
| `poc_feasibility` | easy · moderate · heavy | a CONSTRAINT, not a ranking signal |
| `feasibility_blockers` | list of strings | e.g. ["needs_beacon_fixtures"] |
| `impact_supported` | bool | is the impact source-backed (true) or unsupported drama (false)? |

## Score (deterministic, config weights)
`impact_fit = impact_class_weight + value_at_risk_weight + terminality_weight + recall_delta_bonus +
selector_preservation_bonus`. Award-class impact classes weight high (5–6); skim/dust/local/griefing weight low (1–2).
`poc_feasibility` does NOT enter `impact_fit`.

## Infeasibility (the ONLY reason a high-impact candidate may be deferred)
`DEFER_INFEASIBLE` iff a `feasibility_blockers` entry is in the configured `infeasible_blockers` set:
`source_unavailable` · `dependency_unmockable` · `no_exploit_path` · `no_falsifiable_assertion`. **Harness-weight
blockers** (`needs_beacon_fixtures` · `needs_slashing_setup` · `needs_snapshot_scaffolding` · `needs_fork`) are NOT
infeasible → they set `heavy_poc=true` and route HEAVY/PARTIAL.

## Routing rule (per candidate)
1. If impact is unsupported (`impact_supported=false`) and impact_class is high-drama → do NOT route on drama;
   `DEFER_LOW_IMPACT` (or KEEP_AS_CONTROL) — the anti-drama guard (mirrors P267's refute-first).
2. Else if a genuine infeasible blocker is present → `DEFER_INFEASIBLE` (with the blocker named).
3. Else if `impact_fit >= high_impact_threshold`:
   - `poc_feasibility == heavy` (or a harness-weight blocker) → `SELECT_FOR_PARTIAL_RUNTIME` if a partial runtime is
     plausible, else `SELECT_FOR_MANUAL_HARNESS_DESIGN`. (Both mean: routed, heavy_poc=true — NOT dropped.)
   - else → `SELECT_FOR_FULL_POC`.
4. Else (impact_fit below threshold): low-impact → `DEFER_LOW_IMPACT`; an easy low-impact candidate may be
   `KEEP_AS_CONTROL` only after every high-impact subsystem is represented and control budget remains.

## Anti-easy-PoC rule (hard) + subsystem clustering
- **Anti-easy-PoC:** a lower-impact candidate must NEVER outrank or displace a higher-impact candidate by virtue of
  being easier to PoC. Routing order is by `impact_fit` desc; ties broken toward recall_delta then heavier-but-routed.
- **Subsystem clustering:** for each subsystem with ≥1 high-impact candidate, **at least one representative** is
  routed (FULL/PARTIAL/MANUAL) before any low-impact `KEEP_AS_CONTROL` consumes budget. `poc_budget` caps total
  SELECT_* (default 4); a high-impact subsystem representative is never displaced by an easy control.

## Outcomes
`SELECT_FOR_FULL_POC` · `SELECT_FOR_PARTIAL_RUNTIME` · `SELECT_FOR_MANUAL_HARNESS_DESIGN` · `KEEP_AS_CONTROL` ·
`DEFER_LOW_IMPACT` · `DEFER_INFEASIBLE`. Each decision records impact_fit, decisive dimensions, heavy_poc flag,
why-selected / why-skipped, and (for defers) the blocker.

## Advisory contract + guard
Every decision: `severity:null` · `reportable/submission_ready/concluded/emits_finding/production_routing = false` ·
`status: ADVISORY_TRIAGE_DECISION`. Runtime guard raises (exit nonzero, no output) on any leakage / unknown outcome.
Config validation + malformed/missing input fail closed. Bounded output (≤ `max_candidates`). No answer key.
