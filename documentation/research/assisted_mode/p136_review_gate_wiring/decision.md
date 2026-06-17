# P136 — Decision

## Decision: **ACCEPT_WIRED**

Advisory surfacing is now wired into the pipeline review-gate: existing mechanism-detector hits (incl. all 3
P133 MISS) reach `review_gate.md` automatically as a clearly-separated **NOT-confirmed** advisory section, with
the H-03 deep-pass recommendation, **0 effect on confirmed findings / Validated Findings / severity / gates /
submission**, fully reversible via the master flag, and robust to missing/malformed/disabled/empty context.

### Rubric
- **ACCEPT_WIRED** ✅ — advisory reaches review_gate automatically; gated + reversible; no unsafe promotion;
  confirmed count unchanged; 8 new tests + full suite pass.
- Not ACCEPT_WIRED_EVAL_ONLY: the production-default wiring is itself safe (advisory+report only, research-only
  stays research-only, non-blocking), so no need to restrict to eval/full-audit.
- Not TUNE_AND_RETEST / REVERT_WIRING: no noise/label issue; advisory cannot be mistaken for confirmed; gates
  never blocked.

## Final response

**What changed** — `run_pipeline.sh`: `units_invariant_audit` added to the `coverage_review_gate` battery
(report-only) + `surface_mechanism_advisories.py` called before `generate_review_gate.py` in `full` and
`review-gate` (all `|| true`). `generate_review_gate.py`: new `_advisory_section()` renders a NOT-confirmed
advisory section from `mechanism_advisory_context.json`. +8 tests.

**What stayed unchanged** — all detectors, severity, gates, submission, the confirmed-findings count, and the
Validated Findings table; research-only detectors stay research-only; no config schema change (reuses the master
flag). P130–P135 behavior preserved.

**Wiring points** — `coverage_review_gate()` (units audit) → `surface_mechanism_advisories.py` → `generate_review_gate.py`, in both `full` and `review-gate`.

**review_gate.md rendering** — advisory entries appear only under "## Advisory Context — NOT confirmed (mechanism
detectors)" with a bold advisory_only/submission_ready=false/requires_human_review disclaimer + detector table +
deep-pass recommendations; never in Validated Findings; confirmed count unaffected.

**Safety** — all new pipeline commands non-blocking; gates untouched and still enforce; master gate off → no
section; missing/malformed/disabled/empty context → no section, no error; nothing auto-submitted.

**Tests** — 8 new (focused 21 total) pass; full suite 1607 passed / 2 pre-existing snapshot fails / 4 skipped;
`bash -n run_pipeline.sh` OK; `rank_signal_probe --self-test` OK.

**Integrity** — only `run_pipeline.sh` + `generate_review_gate.py` + the new test changed; active audit restored
to `quantamm-2024-12-eval`; noya state restored (review_gate.md removed; benign `active_step:4` documented).

**Decision** — ACCEPT_WIRED.

**Next recommended phase (P137)** — (a) surface the advisory context in the **dashboard** (a read-only
"Advisory Context — NOT confirmed" panel reading `mechanism_advisory_context.json`); (b) run the
`deep_pass_value_provenance` prompt on the H-03 recommendation to test MISS→confirmed conversion; (c) advance
`semantic_tvl_completeness` toward the research→advisory 5-criteria bar so its H-06 recovery can be surfaced at
production default (currently eval-only).
