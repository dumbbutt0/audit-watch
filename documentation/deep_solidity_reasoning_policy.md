# Deep-Solidity Reasoning Policy

**Depth, not language, was the Recall bottleneck.** On a 100%-Solidity answer key Audit-Watch scored
2 HIT / 1 PARTIAL / 2 ADJACENT / 8 MISS / 0 FP ([[project_recall_eval]]). The misses clustered into
repeatable classes. This policy hardens deep Solidity reasoning **without weakening strictness — it always
prefers `needs_deep_pass` over a thin clear, never mints findings, and never silently clears.**

All new detectors are **advisory recall lenses** (never block, 0 gate FP). They feed two routing rules that
move thin clears on high-value surfaces to `needs_deep_pass` (disposition `assigned`, `assigned_pass=deep`).

## 1. Cross-function / boundary invariant lens (advisory → deep-pass)
`scripts/cross_function_invariant_audit.py` (taxonomy `cross_function_invariant_taxonomy.py`, config
`config/cross_function_invariant_patterns.json`). Unlike per-item lenses it **pairs functions within a
contract**. Families (each two-signal, FP-tight; flags a *candidate*, never asserts a bug):

| family | shape | Recall miss |
|---|---|---|
| `store_key_vs_read_key_divergence` | writer keys with one hash (`toHash`), reader reads with another (`toTracingId`) | H-03 |
| `counter_limit_divergence` | a batch/msg counter incremented with no local limit check; limit enforced elsewhere | H-04 |
| `cross_function_reentrancy` | a `nonReentrant` external-call fn whose post-call state a sibling **non-guarded** fn mutates | H-06 |
| `queue_key_length_bound_divergence` | a compaction/prune loop that can skip pending entries | H-07 |
| `written_consumed_assumption_gap` | state validated/written under one fn's assumptions, consumed by another without them | — |

Output fields per hit: `writer_function, reader_function, written_state, consumed_state, expected_invariant,
observed_mismatch, attacker_entrypoint, downstream_sink, why_local_clear_is_insufficient, required_deep_pass`.

## 2. Special-focus strong-clear rule (`coverage_sweep_write.py`, catch-all)
A clear on a **special-focus** surface may not be a thin one-line local explanation. An item is special-focus
if a high-risk term matches its name/contract/signature/tags (`scripts/special_focus_terms.py` — gateway,
checkpoint, subnet, register, leave, release, lock, collateral, signature, quorum, batch, queue, withdraw,
deposit, refund, retry, actor, supply, circulating, custody, stake, validator, …), OR its attack-surface
score ≥ threshold. Such a clear must carry the deep fields — `attacker_entrypoint`, `cross_function_consumers`,
`downstream_sinks`, `state_transition_ordering`, `value_source_consistency`, plus **conditionally**
`reentrancy_callback_analysis` (if the fn has external calls) and `queue_liveness_analysis` (if it has
loops/batches/releases). Missing → **strict full-audit: `needs_deep_pass` (`incomplete_strong_clear`)**;
advisory: warn.

This rule is a **catch-all that defers to the specialized validators**: it does not fire for
math-estimator-sensitive items (the math-proof rule owns them), dependency-based clears (the
dependency-locality rule owns them), finding-linked items, or **read-only `view`/`pure` getters** (no state
transition / asset movement / reentrancy to analyse — that is where a thin clear is legitimate; the Recall
misses were all state-mutating). Flags: `special_focus_strong_clear` / `_strict` / `_strict_full_audit`.

## 3. Advisory-lens escalation (`scripts/advisory_escalation_gate.py`)
Closes the "advisory hit → routing_gap" (Recall: recipient lens hit `AssetHelper`→H-09, cross-artifact lens
hit `newSubnetActor`→H-08, both ignored). For any **high-risk** advisory hit (cross_artifact_lifecycle,
recipient_custody, griefing_dos, cross_function_invariant, asset_source_consistency, checkpoint_liveness)
whose manifest surface matches the high-risk term set **and** whose current disposition is `cleared`, it
**re-routes that item to `needs_deep_pass`** — never to a finding, never touching non-high-risk hits or
non-cleared items. Strict full-audit only; override `AUDITWATCH_ADVISORY_ESCALATION_OVERRIDE=1`. Runs in
`coverage_review_gate()` **before** the completeness gate, so re-routed items re-open it.

## 4. Asset-source vs amount-origin consistency lens (advisory → deep-pass)
`scripts/asset_source_consistency_audit.py`. Flags a function that mixes ≥2 asset-source families
(collateral / supply / native / token) and moves funds from a source different from the amount's origin
(Recall H-05: `leave()` paid a `genesisBalance` supply amount out of `collateralSource`). Fields:
`amount_origin, asset_source, accounting_state_updated, actual_transfer_source, mismatch,
attacker_controlled_parameter, impact_ceiling`.

## 5. Checkpoint / queue / returndata liveness lens (advisory → deep-pass)
`scripts/checkpoint_liveness_audit.py` (separate from `griefing_dos`, which stays cost-asymmetry). Flags:
`recipient_blocks_checkpoint` (external call inside a checkpoint/batch loop), `unbounded_returndata` (H-09),
`compaction_skip` (H-07), `floodable_state` (M-04, Medium — reported, not auto-escalated).

## Guardrails
No coverage-disposition enum changes (`ALLOWED` untouched). Lenses are advisory (0 gate FP). The only
disposition mutations are `cleared → needs_deep_pass` routings (strict full-audit, overridable) — never a
finding, never a silent clear. No Rust handling here (see the eval report's Rust-readiness recommendation).
