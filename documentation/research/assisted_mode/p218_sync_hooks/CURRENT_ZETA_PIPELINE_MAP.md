# P218 — CURRENT ZETA PIPELINE MAP (where P215 outputs live; what auto-syncs)

| Stage / artifact | Path | Auto-syncs to dashboard? |
|---|---|---|
| Candidate register | `documentation/research/assisted_mode/p215_full_funnel_rehearsal/CANDIDATE_REGISTER.json` | no (input) |
| Merged findings | `audits/zetachain-2023-10-holdout/output/merged_findings.json` | no (input) |
| Deep traces | folded into merged_findings (`_source_agent=deep_trace`) + p215 DEEP_TRACE_RESULTS.md | no (input) |
| Triage outputs | `audits/zetachain-2023-10-holdout/data/triage/{submit,poc_required,downgraded,rejected}.jsonl` | no (input) |
| Confirm outputs | `audits/zetachain-2023-10-holdout/output/{min_confirm_gate.json,confirm/*.json}` | no (input) |
| L3 readiness records | `output_research/l3_readiness/ZETA-*.json` (9/12) | no (input) |
| Report packages | `audits/zetachain-2023-10-holdout/output/submission_pack.{md,json}` | no (input) |
| Dry-run queue | `output_research/dry_run_submission_queue/ZETA-{04,07,12}.json` | no (input) |
| Metrics / scorecard | `…/p215_full_funnel_rehearsal/{metrics.json,ANSWER_KEY_SCORECARD.md,FINDING_MATCHES.md}` | no (input) |
| **Dashboard mirror** | `documentation/research/funnel/synced_findings.generated.json` | **only if the wrapper is run** |
| Dashboard pages | `/findings`,`/candidates`,`/funnel` ← `funnel.load_records()` merge of curated + mirror | reads mirror |

## Steps that do NOT auto-trigger sync today (the P218 gap)
None of the funnel stages call the sync wrapper. After P217 the wrapper exists but is **manual**. There is no
completion check that the mirror is current, so a run can finish with the dashboard stale or a candidate missing.
**P218 closes this: a standalone hook (wrapper + validator) + a completion guard that FAILS unless every candidate is
synced and current.** `run_pipeline.sh` is intentionally not edited (shared across all audits).
