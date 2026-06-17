# P216 — RECOMMENDATION

## DECISION: `DASHBOARD_SYNC_CONTRACT_READY`

### Why
- **One contract, all sources.** `scripts/dashboard_sync.py` converts any candidate bundle (audit_workspace, funnel,
  runtime, detector, campaign, l3, dry_run_queue, future live hunt) into one canonical `synced-1` record that is also a
  valid funnel-1 record. `SYNCED_FINDING_SCHEMA.json` pins the shape.
- **Visible everywhere it should be.** The 12 P215 ZetaChain candidates render in `/findings`, `/candidates`, and
  `/funnel` (12/12 each), and each detail card carries the full **15-section** H5-style verifier checklist — via one
  additive merge in `funnel.load_records()` (the single chokepoint) and one additive resolve in
  `finding_detail._funnel_detail`. No active-audit switch required.
- **Finished-bug parity.** Same `build_verifier_evidence` builder as the Abracadabra H5 card → identical structure and
  safety semantics; content differs honestly (H5 runtime-confirmed vs ZETA mostly NEEDS_HARNESS).
- **Safety held.** 0 records violate any safety flag; `submission_ready`/`routing_allowed` never true; severity is a
  recorded value or `HUMAN_PENDING` (never a conversion token, never browser-computed); missing fields explicit
  (`unknown`/`MISSING_EVIDENCE`); no submit/promote controls; canonical `submission_ready` stays machine-owned.
- **Reproducible.** Generation is idempotent (byte-identical re-run), reversible (delete the mirror), schema-validated,
  no duplicates; backups taken before touching shared files.
- **Tight blast radius.** Only `funnel.py`, `finding_detail.py` (both additive/read-only) and `funnel_records.json`
  (one-time migration to pre-P215 8 records) changed; `deep_trace.md`/`min_confirm_gate.py`/`confirm_gate.py` and all
  other tracked production files byte-identical START==END; `api_free=true` unchanged.
- **Tests.** `tests/research/test_dashboard_sync.py` 16/16: schema · idempotence · no duplicates · safety flags ·
  missing→unknown · P215 visible in all three readers · H5 parity structure · severity never a conversion token ·
  no submit/promote controls · finished-H5 still renders.

### Future routing rule (FUTURE_ROUTING_RULE.md)
Every candidate reaching a meaningful state (confirmed mechanism · needs harness · L3 PASS · L3 FAIL-for-High ·
dry-run-queue entry · human-reviewable Med/High · source-refuted important FP · post-score HIT/PARTIAL/ADJACENT/MISS)
MUST be emitted through the adapter into the mirror; unsynced only if pre-id noise / duplicate scratch / `scratch_only`.

### Limitations / next (human decision, not done)
- The generator currently backfills P215; a thin per-hunt wrapper should call `to_synced_finding` at the end of each
  future hunt/rehearsal/eval so syncing is automatic (the contract + reader already support it).
- Detail richness for sections needing markdown docs (exploit_steps/defense_map) shows `MISSING_EVIDENCE` until a hunt
  supplies inline arrays or artifact docs — by design (honest unknowns), not a defect.
- Optional later: surface `source_track` as a column/filter on the pages (cosmetic; data already carries it).

## ARC
…P214 carve-out wired → P215 full-funnel rehearsal (split visibility) → P216 unified dashboard sync contract: one
read-only synced-finding shape for all sources, P215 backfilled + visible in all three pages, H5-structural parity,
0 safety-flag violations, production blast-radius = 3 intended files.
