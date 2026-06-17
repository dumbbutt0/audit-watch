# P217 — IDEMPOTENCE & REVERSIBILITY

## Idempotence
- `--write` then `--write` (same inputs) → **byte-identical** mirror (`d578cd87…` both runs).
- The `build_synced_findings.py` shim produces the **same** bytes as the wrapper.
- Upsert by `record_id`: re-emitting the 12 ZETA ids replaces their content; unrelated records untouched; de-dup
  guarantees 12 unique ids (no growth on re-run).
- `--dry-run` is side-effect-free: mirror hash unchanged; nothing written.

## Reversibility
- **Backup before every write**: `synced_findings.generated.json.bak.<ts>` (one per write).
- **Remove this phase's records** → pre-P217 state:
  `python scripts/sync_hunt_findings.py --phase P215 --audit zetachain-2023-10-holdout --workspace … --out … --write`
  with `--replace-phase-records` and an empty register drops all `zetachain-2023-10:P215:` records; or simply restore a
  `.bak.<ts>` / delete the mirror (then `funnel.load_records` merges nothing → readers fall back to the 8 curated
  funnel records). No other file depends on the mirror.
- `funnel_records.json` (the curated 8) is **untouched** by P217 — reversibility never disturbs curated data.

## Safety of repeated runs
No run routes/submits/promotes, flips `submission_ready`, or sets `routing_allowed:true`. `--strict` aborts before
writing if any record fails validation. Top-level mirror flags (`research_only/review_only/routes_in_production:false/
is_gate:false`) are re-asserted on every write.
