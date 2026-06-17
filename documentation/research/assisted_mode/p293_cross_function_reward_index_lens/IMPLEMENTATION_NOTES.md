# P293 — IMPLEMENTATION_NOTES

## Files changed (3) — new hashes
| File | Change | new sha256[:16] |
|---|---|---|
| `scripts/research/invariant_delta_deriver.py` | `_lens_reward_index_cross` + helpers (`_l3_hits`, `_l3_pending_in`, `_l3_sibling_pending`, `_l3_share_before_checkpoint`, `_l3_record`) + config families/regexes; swapped one lambda in `derive()`; surface held lens3 reason on the no-deviation branch | see `hash_manifest` below |
| `config/research_invariant_delta_deriver.json` | `lens3_*` term families + status/pattern enums (`_p293_doc`) | — |
| `scripts/research/completion_evidence_deriver.py` | inside the EXISTING lift-upgrade block, fill-if-missing `root_cause`/`runner_up_mechanism` from a P293 lift (scoped to `lens_name == reward_index_cross`; never overrides) | — |

## Kept byte-identical (asserted by test_p293)
`cross_function_value_tracer.py` (f28f0620…), `poc_readiness_evidence_gate.py` (7afdc560…), the P273 router, the
reused 0-FP detector classifiers, and the forbidden 5.

## How the lift happens
1. `_lens_reward_index_cross` returns `REWARD_INDEX_INIT_FOUND` (MEDIUM) on a `LENS3_READY`.
2. `completion_evidence_deriver` already upgrades core dims on any `idr` lift in `lift_statuses` at HIGH|MEDIUM; P293
   additionally fills the two base dims (`root_cause`, `runner_up_mechanism`) that admitted internal-locus packages
   lack — fill-if-missing, scoped to the P293 lens, so no other package changes.
3. The gate lifts past the value-class block via `_id_deviation` (config `lift_statuses`) — no gate edit.

## Why `_lens_reward_index_init` (P289) is untouched
test_p289 calls it directly with the 2-arg signature and asserts MATCH/REFUTE. The new lens calls it FIRST and
returns its result (enriched with lens3 fields) when non-None, so all P289 fixtures + lifts are byte-stable in
behavior; the cross-function path only runs when span-local found nothing.

## Backward-compat / blast radius
- Non-reward candidates: relevance gate returns `None` → `derive()` output identical → no change.
- Other lifting candidates already have `root_cause`/`runner_up_mechanism` set → fill-if-missing is a no-op for them.
- Net behavioral change corpus-wide: exactly ONE new READY (`_increaseUserShare`); one additional lens firing
  (`liquidateUser`) that the gate's D1 holds (`INLINE_GUARD_REFUTED`).
