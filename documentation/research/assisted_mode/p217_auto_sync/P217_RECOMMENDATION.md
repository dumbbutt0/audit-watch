# P217 — RECOMMENDATION

## DECISION: `AUTO_SYNC_READY`

### Why
- **Automation layer exists and is generic.** `scripts/sync_hunt_findings.py` runs at the end of any
  hunt/rehearsal/eval (`--phase/--audit/--workspace/--candidate-register/--l3-dir/--dry-run-queue/--scorecard/--out`
  + `--dry-run/--write/--strict/--replace-phase-records`). It discovers candidates, extracts fields from the real
  artifacts, validates, completeness-scores, and writes the mirror safely. `build_synced_findings.py` is now a thin
  shim over it (single extraction path).
- **Field completeness improved markedly from real artifacts:** **57% → 90%** (144 → 226 / 252), `MISSING_EVIDENCE`
  fields → 0. Newly populated from artifacts: mechanism, root_cause, attacker_model, exploit_steps, function_map,
  defense_map (recommended fix), intent/scope, red_flags. **No invented fields**; the only remaining unknowns
  (`novelty_duplicate`; `l3_status` for the 3 non-L3 candidates) have no source and stay explicit.
- **Safety fully preserved.** 12/12 records pass `validate_synced` + `safety_ok`: `research_only/review_only:true`,
  `routes_in_production/routing_allowed/submission_ready:false`, `no_submit_controls:true`,
  `browser_computes_severity:false`, `canonical_submission_ready_source` present, `human_review_required:true`.
  Severity is recorded-or-HUMAN_PENDING. `--strict` aborts before writing on any violation.
- **Visible + parity.** 12 ZETA in `/findings`, `/candidates`, `/funnel`; ZETA-04/07/11 cards render 15/15 sections now
  with populated mechanism/exploit_steps/defense_map/attacker_model and (ZETA-07) a REPRODUCED PoC; no active-audit
  switch; no submit/promote controls.
- **Idempotent + reversible.** `--dry-run` writes nothing; `--write` is byte-identical on re-run; backup-before-write;
  `--replace-phase-records` / backup restore returns to pre-P217 state; `funnel_records.json` untouched.
- **Tiny blast radius.** Only `build_synced_findings.py` (shim) + the generated mirror changed.
  `dashboard_sync.py`/`funnel.py`/`finding_detail.py`/`findings_overview.py`/`dashboard.py` and the forbidden
  `deep_trace.md`/`min_confirm_gate.py`/`confirm_gate.py` byte-identical START==END. `api_free=true`.
- **Tests.** `test_sync_hunt_findings.py` 14/14 (dry-run writes nothing · write emits 12 · idempotence · safety ·
  completeness ≥85% · unknowns explicit · no invented severity · readers visibility · detail-card sections ·
  no active-audit switch) + full regression suite green.

### How a future hunt uses it
At the end of the hunt, run `sync_hunt_findings.py --phase <Pxxx> --audit <id> --workspace <dir> --write` (or wire that
call into the hunt's finalizer). New phases get their own `record_id` prefix; the mirror is upserted; the dashboard
shows them automatically via the P216 reader merge.

### Limitations / next (human decision, not done)
- Extraction is tuned to the P215 artifact shapes (merged_findings/triage/L3/dry-run-queue/scorecard); a genuinely new
  corpus with different field names would need small per-source adapters (the wrapper is structured for that).
- `novelty_duplicate` stays unknown until a novelty-assessment artifact exists.
- Could add a `--emit-card-markdown` to also write per-candidate evidence docs for sections that prefer markdown.

## ARC
…P215 full-funnel rehearsal → P216 unified dashboard sync contract (one shape, hand-run, many unknowns) → **P217
automation: generic per-hunt wrapper, programmatic field population 57%→90%, idempotent + reversible, 0 safety
violations, blast-radius = shim + mirror.**
