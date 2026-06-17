# P140 — Decision

## Decision: **ACCEPT_PARTIAL_COMPLETION_LOOP**

The completion loop ingests, validates, updates, and renders manual `/deep-pass` results **deterministically,
locally, idempotently, and fail-open**, keeping every completed entry advisory-only (forced triplet) and out of
Validated Findings / the confirmed count. On noya, **1 of 2** queued jobs was completed
(`NoyaValueOracle._getValue` → finding, from the real P137 blind result) and the other
(`SolvencyV2.convertAmountsToValues`) was **honestly left pending** rather than fabricated.

### Rubric
- Not ACCEPT_COMPLETION_LOOP: the mechanism fully works, but not *all* noya jobs were completed (SolvencyV2 left
  pending by design, not fabricated) — the honest label is PARTIAL.
- **ACCEPT_PARTIAL_COMPLETION_LOOP** ✅: ingestion + rendering correct; 1 job completed, 1 pending; 0 rejected.
- Not TUNE_AND_RETEST: schema is clear, the operator workflow is concrete, validation/quarantine is robust, tests
  green — nothing fragile to tune.
- Not REJECT_OR_DEFAULT_OFF: nothing prompt-derived can be mistaken for confirmed/submission-ready — completed
  findings are explicitly "NOT confirmed", excluded from Validated Findings, and gated behind human + PoC.

## Final response

**What changed** — `run_value_provenance_advisories.py` gains `--ingest-results` + a pure `ingest_results()` +
validation/quarantine + an ingestion-report writer; `generate_review_gate.py` renders completed/strong_clear/
finding rows (NOT-confirmed labelling, optional hide-cleared); `config/agent_policy.json` +3 keys; `run_pipeline.sh`
+`--ingest-results || true` ×2; new 16-test file.

**What stayed unchanged** — detectors, severity, submission, gate pass/fail, confirmed count, Validated Findings;
no runner, no API, no new detector; P130–P139 preserved.

**Completion schema** — `job_id`, decision ∈ {finding, likely_exploitable, needs_human, strong_clear, error},
confidence, summaries, `recommended_next_step`, the advisory triplet, provenance paths; forbidden fields
(`submission_ready:true`/`advisory_only:false`/`confirmed:true`/bare `final_severity`) → quarantine.

**Ingestion behavior** — deterministic, local, idempotent, fail-open; matches by `job_id==advisory_id`; flips
pending → completed/failed; forces the advisory triplet; quarantines unsafe/malformed; records accepted/rejected/
unmatched; leaves unmatched + artifact-less pending jobs untouched.

**Review-gate rendering** — advisory-only subsection; finding/likely_exploitable tagged NOT confirmed;
strong_clear shown as cleared advisory context; never in Validated Findings; confirmed count unchanged.

**Noya measurement** — 1 completed (finding, from P137 blind result), 1 pending (SolvencyV2, not fabricated),
0 rejected; confirmed count 0; not in Validated Findings; idempotent re-run; state restored.

**Safety** — all 15 constraints met; forced triplet; fail-open; human + PoC mandatory.

**Tests** — 16 new pass; mechanism_advisory 51 pass; `bash -n` clean; full suite 1637 passed / 2 pre-existing
snapshot fails / 4 skipped; self-test OK.

**Integrity** — only the 5 planned files changed; output/ symlink restored to quantamm-2024-12-eval; noya VP state
restored.

**Decision** — ACCEPT_PARTIAL_COMPLETION_LOOP.

**Next recommended phase (P141)** — complete the second noya job honestly (run the in-session
`deep_pass_value_provenance` skill on `SolvencyV2.convertAmountsToValues`, record + ingest) to convert PARTIAL →
full, and measure across a second architecture (size/blackhole from the P138 corpus) how many queued jobs convert
to finding vs strong_clear vs needs_human — turning the loop into an end-to-end recall/precision instrument while
keeping every output advisory-only.
