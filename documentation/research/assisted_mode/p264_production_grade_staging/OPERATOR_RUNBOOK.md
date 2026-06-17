# P264 — OPERATOR_RUNBOOK
## Run DISABLED (default; safe no-op)
python scripts/research/recall_first_harness.py --out-dir <dir>     # emits nothing, exit 0
## Run SHADOW (advisory)
python scripts/research/recall_first_harness.py --mode shadow \
  --manifest <coverage_manifest.json> --accounting <accounting_checkpoint.json> \
  --state-transition <state_transition_checkpoint.json> --out-dir <dir>
## Files emitted (shadow)
recall_advisory_candidates.json/.md (the bounded advisory set) · recall_metrics.json (observability + version/repro
hashes) · recall_guard_report.json (must be result=PASS, guard_violations=0).
## How to READ advisory candidates
Each is an ADVISORY_RECALL_CANDIDATE = "a locus+mechanism shape worth investigating," NOT a finding. Use
prioritizer_score + sweep_inclusion_reason + templates_applied to triage; bc_ranking_handoff feeds the manual
Profile B/C ranking; generated_mechanisms are interrogative scaffolds (answer the falsification_question).
## What you MUST NOT do
Do NOT treat any advisory candidate as confirmed/reportable/submission-ready/severity-bearing. Do NOT route to the
dashboard as confirmed. Do NOT submit. Promotion requires the SEPARATE B/C ranking → five-op completion → FP
refutation → human review.
## Escalate to human review (shadow)
A candidate may be relabeled READY_FOR_HUMAN_REVIEW_SHADOW only after the downstream stages produce a source-backed
mechanism + ≥PARTIAL chain + passed refutation. Even then it is shadow — a human auditor decides reportability.
## Rollback / disable
Set mode=disabled (default) or remove --mode. See ROLLBACK_PLAN.md.
