# P216 — FUTURE ROUTING RULE (invariant)

**Every** candidate that reaches any of these states MUST be emitted through
`dashboard_sync.to_synced_finding(...)` into `synced_findings.generated.json` (via `build_synced_findings.py` or an
equivalent per-hunt generator), so it appears in `/findings`, `/candidates`, and `/funnel` as a read-only synced card:

- confirmed mechanism
- needs harness
- L3 PASS
- L3 FAIL for a High/Critical target
- dry-run submission-queue entry
- human-reviewable Medium
- human-reviewable High
- source-refuted but important false positive
- post-score HIT / PARTIAL / ADJACENT / MISS

A candidate MAY remain unsynced **only** if one of:
- rejected as pure noise **before** a candidate id is assigned;
- duplicate scratch output of an already-synced candidate;
- explicitly tagged `scratch_only: true`.

## Guarantees the contract enforces on every synced record
- `research_only:true`, `review_only:true`, `routes_in_production:false`, `routing_allowed:false`,
  `submission_ready:false` (canonical submission_ready stays machine-owned by `submission_gate.py`).
- `no_submit_controls:true`, `browser_computes_severity:false`.
- `severity_recommendation` is a **recorded** severity or `HUMAN_PENDING` — never inferred, never a conversion token.
- Missing evidence is explicit (`unknown` / `MISSING_EVIDENCE`).
- L3 status + blockers + dry-run-queue status surfaced; post-answer-key notes ride in `last_reviewer_note` only.

## How to wire a new source (audit workspace / runtime / live hunt / etc.)
Build a bundle (see `DASHBOARD_SYNC_CONTRACT.md` for keys), set `source_track` to the origin, and run the generator.
No reader change is needed — `funnel.load_records()` already merges the mirror. Do **not** hand-append to
`funnel_records.json`.
