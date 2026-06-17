# P269 — IMPLEMENTATION_NOTES

`scripts/research/impact_first_poc_triage.py` + `config/research_impact_first_poc_triage.json`. Deterministic; no
answer key; no source-reading; no network; un-wired; does not import/modify P260/P262/P264/P267.

## Structured input, not award labels
Each candidate carries source-derivable signals (impact_class, recall_delta, subsystem, terminality, value_at_risk,
selector_outcome, poc_feasibility, feasibility_blockers, impact_supported, partial_runtime_plausible). The backtest's
`expected`/award metadata is ignored by the policy (it reads only the candidate fields).

## Scoring + routing (see TRIAGE_POLICY_SPEC)
- `impact_fit = impact_class + value_at_risk + terminality + recall_delta_bonus + selector_preservation_bonus`.
  Award-class classes (slashing/insolvency/bad_debt/snapshot_checkpoint_corruption/liq_redemption_blockage/
  permanent_reward_loss/statemachine_terminal_failure/cross_domain_accounting_mismatch/systemic_liveness_failure)
  weight 5–6; skim/dust/local/griefing 1–2. **`poc_feasibility` is NOT in `impact_fit`.**
- Candidates ranked by `impact_fit` desc (ties → recall_delta → heavier-but-routed → input order).
- **Anti-easy-PoC:** a lower-impact candidate can never displace a higher-impact one for being easier.
- **Harness-weight ≠ infeasible:** `needs_beacon_fixtures` / `needs_slashing_setup` / `needs_snapshot_scaffolding` /
  `needs_fork` / `needs_proof_fixtures` set `heavy_poc=true` and route `SELECT_FOR_PARTIAL_RUNTIME` (or
  `SELECT_FOR_MANUAL_HARNESS_DESIGN`). `DEFER_INFEASIBLE` only for genuine blockers (source_unavailable /
  dependency_unmockable / no_exploit_path / no_falsifiable_assertion).
- **Anti-drama:** a high-`impact_fit` candidate whose `impact_supported=false` is NOT routed on drama → DEFER_LOW_IMPACT
  (mirrors P267's refute-first anti-drama guard).
- **Subsystem clustering + budget:** each high-impact subsystem gets ≥1 routed representative; `poc_budget` (4) caps
  SELECT_*; a low-impact `KEEP_AS_CONTROL` consumes budget only after high-impact subsystems are represented (and is
  demoted to DEFER_LOW_IMPACT if budget is reserved). A new high-impact subsystem is always represented.

## Advisory contract + guard
Every decision hard-stamps `severity:null` + 6 false promotion flags + `status:ADVISORY_TRIAGE_DECISION`. The runtime
guard (`_enforce_guards`) writes a FAIL `triage_guard_report.json` and exits 2 with no decision output on any leakage
or unknown outcome. `_validate_config` fails closed on unsafe research flags / non-positive caps; malformed/missing
input → exit 2. Bounded by `caps.max_candidates`.

## Output
`{decisions:[...]}` JSON + markdown table. Each decision records impact_fit, heavy_poc, decisive_dimensions,
feasibility_blocker, and the outcome. `selected_count` = number routed into the PoC path.
