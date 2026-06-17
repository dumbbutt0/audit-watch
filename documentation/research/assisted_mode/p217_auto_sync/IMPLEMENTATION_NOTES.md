# P217 — IMPLEMENTATION NOTES

## New: `scripts/sync_hunt_findings.py` (generic per-hunt wrapper)
- CLI per `AUTO_SYNC_DESIGN.md`; `main(argv)` is importable (used by tests + the shim).
- Discovers candidate ids from the register; auto-resolves `audits/<audit>/output/merged_findings.json` and
  `data/triage/*` from `--audit`; loads L3 (+ flag-on `decide()`), dry-run-queue, harness (L3 poc_path), scorecard.
- Builds a rich bundle (`build_bundle`) → `dashboard_sync.to_synced_finding` (pure, P216, **unchanged**) →
  `dashboard_sync.validate_synced`. Completeness via `score_record` (21 evidence fields; safety excluded).
- Write semantics: backup before write; upsert by `record_id`; `--replace-phase-records` drops stale phase records;
  `--dry-run` writes nothing; `--strict` aborts on any validation/safety failure. Preserves top-level mirror flags.
- Reuses (no edits): `dashboard_sync` (mapping + safety), `validate_p208_l3_readiness.decide` (L3 verdict),
  `finding_detail.build_verifier_evidence` (already prefers inline sections from P216).

## Why no production-code edits beyond the shim
`to_synced_finding` already accepts `exploit_steps`/`attacker_model`/`defense_map`/`function_map`/`red_flags`/
`root_cause`/`intent_scope_operator_assumptions` and `build_verifier_evidence` already prefers inline sections (P216).
So the completeness jump (57%→90%) comes purely from feeding richer bundles. `dashboard_sync.py`, `funnel.py`,
`finding_detail.py`, `findings_overview.py`, `dashboard.py` are byte-identical START==END.

## `scripts/build_synced_findings.py` → thin shim
Now calls `sync_hunt_findings.main(P215_ARGS + extra)` so there is a single extraction path; running it produces the
byte-identical mirror the wrapper produces (verified). Backward compatible.

## Honest gaps (left explicit, not invented)
- `novelty_duplicate` → `unknown` (no novelty assessment artifact in P215).
- ZETA-02 / ZETA-09 / ZETA-12 have no L3 record (they were Medium/rejected, not High-ceiling) → `l3_status` unknown,
  surfaced as a missing-artifact warning.
- `poc_verification` REPRODUCED only for ZETA-07 (the one executed harness); others `NOT_STARTED`.
