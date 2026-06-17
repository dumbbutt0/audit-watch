# P140 — Completion Result Schema (manual `/deep-pass` artifact)

One JSON file per completed job, dropped into the audit-local dir
**`output/value_provenance_manual_results/*.json`** (configurable via
`auto_run_value_provenance_manual_results_dir`). Matched to a pending job by `job_id == advisory_id`.

## Fields
| Field | Required | Notes |
|---|---|---|
| `job_id` | yes | must equal the queued `advisory_id` (`VP-{contract}.{function}`) |
| `audit_id` | recommended | provenance |
| `contract`, `function`, `file_path` | recommended | provenance (job already carries these) |
| `prompt_name` | recommended | `deep_pass_value_provenance` |
| `execution_mode` | recommended | `manual_in_session` |
| `completed_at` | recommended | ISO-8601; copied verbatim → keeps ingestion **idempotent** |
| `reviewer_or_runner` | recommended | human / operator / subagent label |
| `prompt_decision` | **yes** | one of `finding` · `likely_exploitable` · `needs_human` · `strong_clear` · `error` |
| `confidence` | optional | `low` · `medium` · `high` (or null for needs_human/error) |
| `mechanism_summary` | recommended | one-line mechanism |
| `source_evidence_summary` | recommended | cited source span |
| `rejected_alternatives` | optional | |
| `impact_summary` | optional | hypothesis, non-binding |
| `limitations` | optional | e.g. "PoC recommended" |
| `recommended_next_step` | optional | `human_review` · `build_poc` · `map_defenses` · `reject` · `keep_advisory` |
| `advisory_only` | **yes / true** | |
| `submission_ready` | **yes / false** | |
| `requires_human_review` | **yes / true** | |
| `source_result_path` | recommended | path to the saved prompt output |
| `raw_output_path` | optional | raw transcript |

## Forbidden (→ quarantined, job left pending)
- `submission_ready: true`
- `advisory_only: false`
- `requires_human_review: false`
- `confirmed: true`
- `final_severity` present **without** an explicit `final_severity_non_binding: true` (or a non-binding/hypothesis
  label) — a bare severity is treated as an attempted promotion and rejected.
- invalid `prompt_decision` / `confidence` / `recommended_next_step` value, or missing `job_id`.

## Merge guarantees
On accept, ingestion **forces** `advisory_only=true / submission_ready=false / requires_human_review=true` on the
merged entry regardless of artifact contents (defense-in-depth: ingestion can only ever flip the triplet the safe
way). `auto_run_status` → `completed` (or `failed` when `prompt_decision==error`). Nothing is confirmed; no
severity is assigned; the entry never enters Validated Findings.
