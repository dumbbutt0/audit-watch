# P129 — Ground-Truth Inventory

## Schema decision (no new schema invented)
The repo already has the right schemas; P129 reuses them rather than building a third:
- **Outcome records** → existing `ground_truth.jsonl` schema (written only by
  `ingest_ground_truth.write_outcome`). Fields used: `finding_id, source_audit, title, vuln_type,
  claimed_severity, agent, ground_truth_outcome, ground_truth_severity, evidence_class, source_file,
  evidence_summary, confidence, recorded_by, recorded_at, duplicate_of_report`.
- **Awarded-issue / match records** → the repo's `awarded_map.json` / `match_matrix.json` convention
  (id, severity, contract, function, classification, matched_ids, reason). The user's requested fields
  (`surfaced`, `surfaced_candidate_id`, `match_type ∈ exact/same_function/same_root_cause/partial/
  adjacent/missed`, `severity_prediction`, `severity_correctness`) are already expressed by these
  artifacts' `classification`/`matched_ids`/`mechanism_naming` fields. Holdout denominators
  (`holdout_awarded_inventory.json`) carry `surfaced`/`match_type = PENDING_RUN`.

No field was fabricated. Unknown fields are left empty/`PENDING_RUN`.

## Beanstalk ground truth written (15 records) — `audits/beanstalk-2024-05/data/evaluation/ground_truth.jsonl`
All `evidence_class=platform_confirmed`, `recorded_by=contest_result`,
`source_file=evals/beanstalk_finale/match_matrix.json`.

| finding_id | outcome | gt_severity | claimed_sev | basis |
|---|---|---|---|---|
| US-001 | accepted | high | Critical | HIT (L2 migration mass-reissue cluster) |
| AC-001 | accepted | high | High | HIT (auth boundary) |
| BSA-001 | accepted | medium | High | HIT |
| EA-001 | accepted | high | High | HIT (economic / L2 migration) |
| FL-001 | accepted | high | High | HIT |
| LG-001 | accepted | high | High | HIT |
| SN-001 | accepted | high | High | HIT |
| BSA-003 | accepted | high | Medium | HIT |
| CC-002 | accepted | high | Medium | HIT |
| AC-003 | accepted | medium | Low | HIT (wrong typehash) |
| DS-003 | accepted | medium | Low | PARTIAL |
| PC-001 | accepted | high | Low | HIT (L2 migration cluster) |
| AR-001 | invalid | invalid | High | scorecard `pipeline_only_FP` — speculative reachability |
| EA-002 | invalid | invalid | Medium | scorecard `pipeline_only_FP` — no awarded counterpart |
| AR-002 | duplicate | medium | Medium | match_matrix `merged_dups`: AR-002 → DS-003 |

## Routed to `needs_human_review.jsonl` (2 records — ambiguous, not guessed)
| finding_id | reason |
|---|---|
| AC-002 | match_matrix ADJACENT (sub 320) — near-miss; human must decide HIT credit |
| SG-001 | match_matrix ADJACENT (sub 505) — near-miss; human must decide HIT credit |

## Not ingested (honest exclusion)
29 of the 44 `merged_findings` entries (mostly `AM-*` low/info, `TI-*`, `SC-001`, `DS-001/2`) have **no
committed answer-key classification** → not graded (no verdict to transcribe). Recorded here as excluded,
not labelled.

## Faithful triage reconstruction (why, and exactly what)
`beanstalk/data/triage/` was **empty** (the eval ran via the independent path). `compute_metrics` and
`evaluate_pipeline_accuracy` resolve the pipeline *decision* from triage buckets. To avoid emitting a
misleading 0.0, decisions were reconstructed **only for the 15 verdicted findings, from
`merged_findings.json` (= the pipeline's actual promoted set)**:
- `submit.jsonl` — the 14 promoted+verdicted findings (12 valid + 2 FP), each tagged
  `recommended_severity` = the pipeline's claimed severity and `_reconstructed_from` provenance.
- `merged.jsonl` — AR-002 (the internal duplicate).
Each entry is defensible: being in `merged_findings.json` means the pipeline promoted it. No outcome or
severity was invented; the FP/valid labels come from the committed scorecard/matrix, not the bucket.

## Holdout denominators — `holdout_awarded_inventory.json`
centrifuge (8M) · pooltogether (1H/8M) · predy (4H/8M) · zetachain (14H/34M) = 77 awarded issues,
each with `issue_id, awarded_severity, title, source URL, evidence_path`, and
`surfaced=match_type=PENDING_RUN` (no local pipeline output to match).
