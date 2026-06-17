# P218 — HOOK IMPLEMENTATION

## `scripts/run_hunt_sync_hook.py` (mandatory completion step)
```
python scripts/run_hunt_sync_hook.py --phase <Pxxx> --audit <id> --workspace <dir> \
   [--candidate-register P] [--l3-dir D] [--dry-run-queue D] [--scorecard P] \
   [--out <mirror>] [--metrics <sync_hook_metrics.json>] [--skip-live]
```
Order: (1) `sync_hunt_findings.main(--write --strict)` regenerates the mirror from real artifacts; (2) write sync
metrics; (3) `validate_hunt_sync_completion.main(--strict)`; (4) update metrics with the guard rc. **Exits non-zero if
either step fails** → a hunt cannot be "complete" with a stale/incomplete dashboard.

**Writes ONLY:** `documentation/research/funnel/synced_findings.generated.json` (via the wrapper, backup-first) and
`output_research/funnel/sync_hook_metrics.json`. (Plus the P218 docs + tests, which are this phase's deliverables.)
**Never** touches route/submit/promote code, `runtime_policy.json`, the curated `funnel_records.json`, or audit source.
Idempotent (byte-identical mirror on re-run); logs exactly what was synced.

## `scripts/validate_hunt_sync_completion.py` (completion guard)
```
python scripts/validate_hunt_sync_completion.py --phase <Pxxx> --audit <id> --workspace <dir> \
   [--candidate-register P] [--synced-mirror M] [--l3-dir D] [--dry-run-queue D] \
   [--metrics M] [--strict] [--allow-extra] [--skip-live] [--report out.json]
```
Pure `run_checks(candidates, synced_records, drq_ids, opts)` (testable) + live `check_readers` / `check_cards`
(injectable). Emits a JSON report; exits non-zero on any failure (or warning under `--strict`). See
`SYNC_COMPLETION_VALIDATION.md` for the check list and example reports.

## Why standalone (not wired into run_pipeline.sh)
`run_pipeline.sh` is shared across ALL audits; wiring the research sync there would fire it for unrelated production
audits (the spec's warned-against side effect). P218 ships the hook as the **required documented completion command**
+ the guard a phase must pass — exactly the spec's "no safe central runner → document the required command" fallback.
`run_pipeline.sh` is byte-identical START==END.

## Live run (REPLAY_MODE)
`run_hunt_sync_hook.py --phase P215 --audit zetachain-2023-10-holdout --workspace …/p215_full_funnel_rehearsal`
→ exit 0; wrapper wrote 12 (byte-identical), guard PASS, metrics: 12 records / 90% / safety_ok / completion_ok.
