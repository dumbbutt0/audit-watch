# P267 — IMPLEMENTATION_NOTES

`scripts/research/mechanism_pairwise_selector.py` + `config/research_mechanism_pairwise_selector.json`. Deterministic;
no answer key; no source-reading; no network; un-wired (no run_pipeline/agent_policy/dashboard reference); does not
import or modify P260/P262/P264.

## Why structured inputs (not an LLM that reads source)
The selector consumes per-mechanism **dimension signals** an auditor states pre-reveal (impact_class, value_at_risk,
victim/gainer clarity, intent_violation, attacker_control, persistence, refutation_resistance, poc_feasibility).
This keeps the module deterministic and reproducible, and — crucially — keeps award labels OUT of the decision. The
backtest's `awarded_is`/`expected` fields are ignored by the selector (it only reads `M1`/`M2`).

## Scoring
- `terminal_impact = impact_class_weight + value_at_risk_weight + persistence_weight`. Award-like classes
  (permanent_dos/insolvency/stranded_funds/reward_loss/blocked_liquidation_redemption/accounting_corruption/
  liveness_failure) weight 5–6; one_off_skim/dust_rounding/local_misprice weight 1–2.
- `validity = attacker_control + refutation_resistance(refuted = −5) + intent_violation + victim_gainer_clarity`.
- `plausible = (refutation_resistance != refuted) and (attacker_control != none)`.

## Decision rule (see SELECTOR_SPEC for full text)
Terminal impact is the **primary axis**. Key behaviors:
- **Refuted high-impact → REFUTE_FIRST** (a dramatic but refuted mechanism never auto-wins — anti-drama guard).
- **anti_easy_poc_flag** = the higher-impact mechanism is *harder* to PoC than the lower-impact rival (the P266
  trap). When set, the outcome is forced to `SELECT_high` or `KEEP_BOTH` — **never** `SELECT_low`.
- **Material gap + both plausible → KEEP_BOTH** (protect the high-impact mechanism; carry both to PoC).
- **High-impact dominant + rival weak → SELECT_high.**
- **Near-equal impact:** one refuted → select the other; both plausible → KEEP_BOTH; else INSUFFICIENT_EVIDENCE.
- **Fail-closed:** unresolved → INSUFFICIENT_EVIDENCE.
`poc_feasibility` is never a positive selection driver — it can only raise the anti-easy-PoC flag or nudge toward
KEEP_BOTH. This is the precise inversion of the P266 failure (where feasibility drove selection).

## Advisory contract + guard
Every decision hard-stamps `severity:null` + 6 false promotion flags + `status:ADVISORY_SELECTOR_DECISION`. A runtime
guard (`_enforce_guards`) scans all decisions and, on any leakage or unknown outcome, writes a FAIL
`selector_guard_report.json`, raises, exits 2, and emits NO decision output. Config validation (`_validate_config`)
fails closed on unsafe research flags or non-positive caps. Malformed/missing input → exit 2 (verified).

## Output
`{decisions:[...]}` JSON + a markdown table. Each decision records per-mechanism terminal_impact/validity/plausible,
impact_gap, anti_easy_poc_flag, outcome, decisive_dimensions, uncertainty, and the two falsification questions.
Bounded by `caps.max_pairs` (50).
