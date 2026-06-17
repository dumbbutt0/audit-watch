# P217 — AUTO_SYNC DESIGN (per-hunt sync wrapper)

## Goal
A generic, reusable tool any future hunt/rehearsal/eval calls at the end to route its candidates into the dashboard
mirror with fields populated from the real artifacts — no hand-editing, safety preserved.

## File: `scripts/sync_hunt_findings.py`
Generic (not P215-hardcoded). Reuses `dashboard_sync.to_synced_finding` + `validate_synced` (P216) as the pure mapping;
the wrapper only does **artifact discovery + extraction + completeness scoring + safe write**.

### CLI
```
sync_hunt_findings.py
  --phase P215                 # provenance tag + record_id prefix
  --audit zetachain-2023-10-holdout   # resolves audits/<audit>/output/merged_findings.json + data/triage/*
  --workspace documentation/research/assisted_mode/p215_full_funnel_rehearsal
  --candidate-register <path | default: <workspace>/CANDIDATE_REGISTER.json>
  --l3-dir output_research/l3_readiness
  --dry-run-queue output_research/dry_run_submission_queue
  --scorecard <path | default: <workspace>/ANSWER_KEY_SCORECARD.md>
  --out documentation/research/funnel/synced_findings.generated.json
  # modes
  --dry-run                    # print plan + completeness, write NOTHING
  --write                      # write the mirror (backup first)
  --strict                     # exit nonzero if any record fails safety/schema validation
  --replace-phase-records      # drop existing mirror records sharing this phase/audit prefix not in this emit
```

### Pipeline (per candidate id discovered from the register)
1. Load: register row · merged finding (`audits/<audit>/output/merged_findings.json`) · triage record (scan
   `data/triage/{submit,poc_required,downgraded,rejected}.jsonl`) · L3 record (`<l3-dir>/<id>.json`) + `decide()`
   (flag-on, no persist) · dry-run-queue record (`<dry-run-queue>/<id>.json`) · harness (from L3 `poc_path`/`pocs/`) ·
   scorecard verdict (parse `<scorecard>` + sibling `FINDING_MATCHES.md` for lines mentioning the id).
2. Build a **rich bundle** per `FIELD_POPULATION_MAP.md` (absent ⇒ `unknown`/`MISSING_EVIDENCE`, never invented).
3. `rec = dashboard_sync.to_synced_finding(bundle)`; `errs = dashboard_sync.validate_synced(rec)`.
4. Completeness-score the record (21 evidence fields; safety defaults excluded).

### Write semantics (safe)
- Load existing mirror; **upsert by `record_id`** (same id ⇒ replace content); de-dup; preserve unrelated records.
- `--replace-phase-records`: additionally drop existing records whose `record_id` starts with the phase/audit prefix
  but are absent from this emit (handles removed/renamed candidates).
- **Backup** mirror to `…json.bak.<ts>` before any write. `--dry-run` writes nothing.
- Refuses to write if any record fails validation under `--strict`; otherwise warns and skips the bad record.
- Top-level mirror flags preserved (`research_only/review_only/routes_in_production:false/is_gate:false`).
- **Never** writes route/submit output; never flips `submission_ready`/`routing_allowed`.

### Output (printed)
records emitted · updated · unchanged · missing-artifact warnings (per id, which sources were absent) ·
field-completeness (per record + aggregate, before vs after if a prior mirror exists) · safety validation result ·
mirror output path.

## Reuse
- `dashboard_sync.to_synced_finding` / `validate_synced` — pure mapping + safety gate (unchanged).
- `validate_p208_l3_readiness.decide` — L3 verdict (flag-on, read-only) for `high_promotion_allowed`/blocker/calibrated.
- `funnel.normalize_record` is NOT called here (the mirror stores raw synced-1 records; `funnel.load_records` normalizes
  on read).

## `build_synced_findings.py` (P216) → thin shim
Refactored to call `sync_hunt_findings.main(["--phase","P215","--audit","zetachain-2023-10-holdout",…,"--write"])` so
there is a single extraction code path and no stale lower-fidelity generator can downgrade the mirror.

## Safety invariants (enforced by `validate_synced`, re-checked here)
`research_only:true` · `review_only:true` · `routes_in_production:false` · `routing_allowed:false` ·
`submission_ready:false` · `no_submit_controls:true` · `browser_computes_severity:false` ·
`canonical_submission_ready_source` present · `human_review_required:true`. Severity is recorded-or-`HUMAN_PENDING`,
never inferred. Run fails (`--strict`) on any violation.
