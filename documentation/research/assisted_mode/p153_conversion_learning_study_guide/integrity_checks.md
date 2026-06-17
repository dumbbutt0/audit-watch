# P153 — Integrity Checks

P153 is a **lesson-summary / learning-analysis** phase. It produces documentation only. The checks
below establish that no production, harness, prompt, detector, gate, routing, severity, submission,
corpus, sidecar, or active-audit-symlink state was changed, and that the deliverable is grounded.

## Claims and how each is verified

| Claim | Verification |
|---|---|
| **Only docs added** | The phase writes exactly three files, all under `documentation/research/assisted_mode/p153_conversion_learning_study_guide/`: `STUDY_GUIDE.md`, `metrics.json`, `integrity_checks.md`. No file under the production tree was edited. |
| **No new vulnerability candidate** | The guide introduces no candidate; it summarizes the six existing sidecar rows (B1, B5, H1–H4) and adds no row to any corpus or sidecar. |
| **Sidecar unchanged** | `output_research/value_provenance_eval/runtime_status.jsonl` was **read only**; the conversion table + funnel are transcribed verbatim from it. No write. |
| **Prompt baseline byte-for-byte unchanged** | No change to the prompt corpus or harness; full `pytest -q` expected unchanged (1673 passed / 2 pre-existing snapshot fails / 4 skipped). |
| **No detector/gate/routing/severity/submission change** | No edits to `run_pipeline.sh`, `config/*`, `scripts/*`, or `audits/*/contracts`. |
| **Harness stays un-wired** | `grep value_provenance_eval_harness run_pipeline.sh config/agent_policy.json` expected empty (unchanged from prior phases). |
| **All rows routing_allowed=false / submission_ready=false** | The guide asserts this and the sidecar rows already carry it; nothing was flipped. |
| **runtime_status vs conversion_outcome preserved** | §5 defines them as separate axes; §10 lists both columns; the H4 note preserves the sidecar nuance (`conversion.blocker=null` vs `primary_blocker_if_not_reportable=mechanism_absent_guard_present`). |
| **Unknowns marked unknown** | Phase 0–~99 and unlisted P100–P116 specifics are marked "(reconstructed; exact per-phase detail unknown)"; H1 attacker_reachable/severity_bearing/reportable are `unknown`. |
| **No submission-readiness claim** | The guide's footer and `metrics.json` set `submission_ready: false`. |

## Funnel transcription (verbatim from the sidecar)

- Panel: **15 rows** = 11 corpus rows overlaid + **4 runtime-only** (H1–H4).
- by_status: **runtime_confirmed 4** (B1, B5, H1, H3) · **runtime_refuted 2** (H2, H4) · **not_run 9**.
- **reportable_candidate_needs_human_review = 0** · **submission_ready = 0**.
- B1/B5 are corpus duplicate-known rows → outside the conversion funnel (no conversion object).

## Active audit

`output/` symlink unchanged → `quantamm-2024-12-eval`. No `audit_manager.py switch` performed.
