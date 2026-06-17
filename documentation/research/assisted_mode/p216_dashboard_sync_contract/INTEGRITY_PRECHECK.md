# P216 — INTEGRITY PRECHECK (START)

**Captured:** 2026-06-07, before any change. md5 first-8.

| File | START | expected at END |
|------|-------|-----------------|
| `scripts/dashboard.py` | `197ac4d5` | unchanged |
| `scripts/findings_overview.py` | `5c6cccb5` | unchanged |
| `scripts/funnel.py` | `14f1e1c7` | **CHANGE** (additive 2nd-file merge in `load_records`) |
| `scripts/candidate_detail.py` | `da925496` | unchanged |
| `scripts/finding_detail.py` | `0c05f470` | **CHANGE** (additive inline-section preference in `build_verifier_evidence`) |
| `scripts/submission_readiness_review.py` | `e4960878` | unchanged |
| `scripts/final_submission_pack.py` | `57cba16d` | unchanged |
| `documentation/research/funnel/funnel_records.json` | `99f5a6a7` | **CHANGE** (one-time migration → restored to pre-P215 8 records) |
| `config/runtime_policy.json` | `bea43487` | unchanged |
| `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` | unchanged |
| `prompts/deep_trace.md` | `ef93a6c2` | unchanged (forbidden) |
| `scripts/min_confirm_gate.py` | `41dd3c96` | unchanged (forbidden) |
| `scripts/confirm_gate.py` | `4fadfc5f` | unchanged (forbidden) |

## Confirmed preconditions
- `config/runtime_policy.json` → `api_free: true`.
- No live route-to-submit exists (verified P215: all submission code is local draft-only).
- No dashboard submit/promote controls (verified: `/findings`, `/candidates`, `/funnel` HTML are GET-only, explicit
  "nothing here routes, sets severity, or marks anything submittable"; no `<button>`/`<form>`/POST).
- Canonical `submission_ready` remains machine-owned (`submission_readiness_review` is append-only advisory; the
  detail card forces `submission_ready:false`/`routing_allowed:false`).
- Active audit currently `zetachain-2023-10-holdout` — **irrelevant** to this task: `/findings`, `/candidates`,
  `/funnel` read the **global** research funnel track, not the active audit. P216 will be verified without switching.

## Migration backup
Pre-P215 curated funnel records (8): `documentation/research/funnel/funnel_records.json.bak.20260607T050647Z`
(the migration restores this; the 12 P215 rows move to the generated mirror).

## Scope guarantee
Only `funnel.py`, `finding_detail.py` (both additive/read-only) and `funnel_records.json` (data migration) change among
tracked files. All other production files byte-identical START==END.
