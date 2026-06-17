# P216 — WRITER DESIGN

## Where synced records live
`documentation/research/funnel/synced_findings.generated.json` — a **generated read-only mirror** (schema_version
`synced-1`; top-level `research_only:true`, `review_only:true`, `routes_in_production:false`, `is_gate:false`). Kept
**separate** from the hand-curated `funnel_records.json` so curated vs generated never mix.

## Writer
`scripts/build_synced_findings.py` (CLI). For each candidate it assembles a bundle from recorded artifacts and calls
`dashboard_sync.to_synced_finding` + `validate_synced`, then writes the mirror.
- **Backup before write:** copies the existing mirror to `…json.bak.<ts>` before overwriting.
- **Idempotent:** drops any prior records whose `record_id` starts with the P216 prefix, de-dups by `record_id`
  (last wins); re-runs are byte-identical (verified).
- **Schema-validated:** refuses to write if any record fails `validate_synced` (enums + the 8 safety flags +
  "severity is recorded or HUMAN_PENDING").
- **No duplicates / reversible:** delete the mirror (or the prefixed records) to revert; nothing else depends on it.
- **No writes to shared curated files** and no routing/submission.

## Reader integration (one additive change)
`scripts/funnel.py` `load_records()` — after reading `funnel_records.json`, additively merges
`SYNCED_RECORDS_PATH` (`synced_findings.generated.json`) into `raw_findings` (guarded; missing file = no-op; dedup by
`record_id`). This single chokepoint feeds `/funnel` (`api_funnel`), `/findings` (`findings_overview._load_funnel`) and
`/candidates` (`findings_overview.load_overview`). Backward compatible: the 8 curated records still load.

## Detail-card parity (one additive renderer change)
`scripts/finding_detail.py` `_funnel_detail()` — `load_records()["records"]` are whitelisted display **rows** that drop
rich detail fields, so the card resolves the **full normalized record** (curated + mirror) and merges it under the row
before `build_verifier_evidence`. Read-only; never touches severity (`_sev_or_status` unchanged), `submission_ready`,
or `routing_allowed`. `build_verifier_evidence` additionally prefers inline synced sections
(`exploit_steps`/`defense_map`/`attacker_model`/`function_map`/`red_flags`) when present.

## Migration (one-time, documented)
`funnel_records.json` was restored to its pre-P215 backup (8 curated records); the 12 P215 ZETA candidates were
re-emitted through the adapter into the mirror — so they are no longer hand-curated and there are no duplicates.
Backups retained: `funnel_records.json.bak.20260607T050647Z` (pre-P215) and `…bak.pre-p216.<ts>` (the 20-record state).
