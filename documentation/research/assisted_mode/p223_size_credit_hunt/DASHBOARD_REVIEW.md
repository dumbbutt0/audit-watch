# P223 — Dashboard review (Step 8)

## Read-only posture (verified)
- `scripts/dashboard.py` byte-identical START==END (`9de16b68`, the P222-verified build). Its POST routes are
  research/dashboard controls (audit switch/create, pipeline run, validation labels, advisory
  submission-readiness) — **none** perform external submission or auto-route; no route sets a canonical
  `submitted=true` / `routing_allowed=true` to any platform. The server was not launched (flaky in this harness,
  per prior phases); read-only verification is via the byte-identical hash + route inspection.
- The dashboard's `_build_state` reads the **active audit** (`size-credit-2024-06-blind`) workspace
  (`output/merged_findings.json`, triage, status) — so P223 findings render in the active-audit views without
  any mutation.

## Shared dashboard mirror — deliberately NOT mutated
The global synced-findings mirror `documentation/research/funnel/synced_findings.generated.json` remains
byte-identical (`bcf4c1c1`, the P222 END state). The P217/P218 `run_hunt_sync_hook` / `sync_hunt_findings`
wrapper is tuned to the P215 **ZETA** corpus and, per the P217 notes, needs a **per-source adapter** for a new
corpus (different field names). Running it for the SC-* corpus would (a) require that adapter and (b) mutate a
P222 tracked deliverable. Both conflict with this phase's isolation + byte-identical invariants, so the shared
sync was intentionally skipped. **Deferred follow-on (human):** add a Size-Credit source adapter to
`sync_hunt_findings.py`, then sync SC-* into the shared mirror. The P223 review artifacts in the meantime are
the active-audit dashboard state + `output/submission_pack.{md,json}` + the dry-run queue + the L3 records.
