# P245 — Build Report: Coverage + Reasoning-Depth Gate (options #3 + #4)

Implements the P244-approved, **default-off** process gate as minimal additive deltas over existing
machinery. No detector family, no severity/routing/dashboard/prompt changes, no schema migration,
forbidden files byte-identical, active audit untouched.

## Final verdict

# A — READY_FOR_DEFAULT_OFF_USE

The gate ships default-off, preserves the existing workflow exactly when off (Arm A + 17 pre-existing
coverage tests green), and when enabled demonstrably catches both P241 failure modes on real nextgen
data: it blocks triage on the unread NextGenCore/MinterContract surface that hid H-01, and reroutes the
shallow create-time-reentrancy rejection instead of dropping it. Operator burden is bounded by an
FP-controlled critical predicate (read-only getters excluded), and the depth gate fires only on
sensitive-area rejections. See `VALIDATION_NEXTGEN.md`, `OPERATOR_BURDEN.md`, `SAFETY_REPORT.md`.

## What shipped

### New pure classifiers (mirror `gate_dos_utils.py`: no I/O, never mint a finding)
- **`scripts/read_completeness_utils.py`** — `ALLOWED_READ_STATES` (the 8 states), `is_critical(item)` /
  `critical_reasons(item)` (predicate over existing manifest fields: state-mutating public/external
  entrypoints, privileged/admin, fallback/receive, hooks/callbacks, token/settlement/oracle/reward/
  liquidation/upgrade paths, facets/selectors, module/guard), `read_state_satisfies_critical(disp)`.
  **FP control:** a bare `public view` getter is NOT critical on its own (would explode the critical
  set); risky getters are still caught via their category (e.g. an `oracle`-tagged getter).
- **`scripts/reasoning_depth_utils.py`** — `SENSITIVE_AREAS` (the 11 areas), `sensitive_areas(decision)`
  (explicit field first, else conservative text classification), `DEPTH_FIELDS` (6), `depth_record_complete`,
  `classify_rejection` → `{not_sensitive | ok | needs_depth}`, `reroute_reason`.

### #3 — coverage gate extension (all default-off)
- `scripts/coverage_completeness_gate.py`: new `--enforce-read-completeness` flag; enables via flag OR
  `coverage_policy.enforce_read_completeness` (+ `_full_audit`). When enabled, each in-scope **critical**
  item whose `read_state` is not satisfied is **blocked** (via the existing override-aware `block()`),
  non-critical unread items only **warn**. New `read_completeness` block in `coverage_gate.json`.
  **No-op when disabled.**
- `scripts/init_coverage_dispositions.py`: seed `read_state="NOT_IN_SCOPE"` for out-of-scope, `None` for
  in-scope (additive; existing records preserved).
- `scripts/update_coverage_disposition.py`: optional `read_state` + `read_block_reason` / `read_block_ack`
  / `duplicate_of` / `generated_interface_reason` (apply_update + CLI), validated against
  `ALLOWED_READ_STATES`.
- `config/agent_policy.json → coverage_policy`: `enforce_read_completeness:false`,
  `enforce_read_completeness_full_audit:false`.

### #4 — rejection depth-record enforcement (default-off)
- `scripts/triage_write.py`: extends the existing no-silent-clear block. When
  `coverage_policy.rejection_depth_record_enforced` is true and a `rejected` candidate touches a sensitive
  area without a complete depth record, it is rerouted to `human_review_queue.jsonl` (`needs_depth=True`,
  `reroute_reason`, `sensitive_areas`, `missing_depth_fields`) — preserved, never silently dropped, never
  minted/relabelled. **No-op when disabled or non-sensitive.**
- `config/agent_policy.json`: `rejection_depth_record_enforced:false`.

## Deliberate scope decisions
- **`run_pipeline.sh` NOT edited.** The gate reads the policy flag directly, so the `coverage-gate`
  command already honors `enforce_read_completeness` with zero shell change — lower risk, fewer edits.
- **#4 implemented in `triage_write.py` only** (the api-free default path). The API `triage_findings.py`
  path is untouched (editing it risks a prompt rewrite — out of P245 scope); noted as a future parallel
  hook.
- **No new disposition status / no manifest schema change.** `read_state` is an orthogonal optional field;
  the critical predicate is computed at gate time from existing fields (P244 Δ-A3 not needed).

## Tests
- `tests/coverage/test_read_completeness_gate.py` (6) + `tests/reasoning_depth/test_rejection_depth_record.py`
  (5) = the 8 required behaviors. Pre-existing `tests/coverage/test_coverage_gate.py` +
  `test_scope_ingestion.py` + `test_specialist_coverage_gate.py` (17) still green (default-off compat).
- `tests/research/test_p245_coverage_reasoning_gate_build.py` — docs guard.
