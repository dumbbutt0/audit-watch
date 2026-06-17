# P210 — no-submit guard

The L3 readiness path is advisory-only and cannot submit/route/promote. Enforced by construction + tests.

## By construction
- `l3_evaluate()` is a pure function returning a dict with `research_only:true` / `routing_allowed:false`; it never
  writes files, never sets `submission_ready`, never imports a router/submit module. It only calls the pure P208
  `decide()`.
- `evaluate()` only appends a string to `failed[]` (a blocker reason). `record_review()` is unchanged in its
  flag-flipping behavior — it still never sets `submission_ready`/`routing_allowed=true` and only ever writes the
  append-only readiness ledger.
- Dashboard attaches a read-only display dict; no controls, no flag writes.

## By test (`tests/research/test_l3_readiness.py`)
- `test_l3_outputs_are_advisory_only` — output has `research_only=True`, `routing_allowed=False`, no `submission_ready`.
- `test_l3_source_has_no_submit_or_route_calls` — the L3 source region contains none of
  `submission_ready = True`, `routing_allowed = True`, `final_submission_pack`, `route(`, `submit(`.
- `test_record_review_never_sets_canonical_flags` — the "never set true" invariant + `routing_allowed:False` remain.
- `config/runtime_policy.json api_free=true` unchanged; no live route enabled.
