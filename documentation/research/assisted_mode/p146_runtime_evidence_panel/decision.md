# P146 — Decision

## Decision: **ACCEPT_RUNTIME_PANEL**

A research-only runtime evidence panel was added to the P142 scorecard, **supplemental** to the prompt-derived
metrics. It backfills B1 and B5 as `runtime_confirmed`/`high` from the runtime sidecar and defaults the other 9
corpus items to `not_run`/`none`. The prompt-derived metrics (`per_arch`/`totals`/`runs`) are **value-for-value
unchanged** (proven by an empty-vs-full-sidecar integrity test and a live baseline reproduction), every panel row
is forced `routing_allowed=false`/`submission_ready=false`, and the harness remains un-wired. No production file
was touched.

### Rubric
- **ACCEPT_RUNTIME_PANEL** ✅: panel added; prompt metrics value-for-value unchanged; B1/B5 backfilled; others
  not_run; research-only + routing_allowed:false throughout.
- Not TUNE_AND_RETEST: schema/vocab/tests are stable (20 passed).
- Not REJECT: the panel cannot perturb prompt metrics (derives from corpus + sidecar only) and cannot
  route/submit (flags forced false).

## Final response

**What changed** — `value_provenance_eval_harness.py` gains `build_runtime_panel` + `runtime-panel` subcommand +
an additive `runtime_panel` key in `scorecard.json` (+ `runtime_panel.json` + a scorecard.md section); the
research-only sidecar B1/B5 rows enriched with the full P146 field set; research config gains `runtime_status_path`;
+6 tests.

**What stayed unchanged** — prompt metrics (`per_arch`/`totals`/`runs`, value-for-value), routing, severity,
submission gates, detectors, all production files; harness un-wired; P130–P145 preserved.

**Schema** — runtime_status ∈ {not_run, partial, runtime_confirmed, runtime_refuted, inconclusive};
runtime_confidence ∈ {none, low, medium, high}; the 17 per-row fields of requirement 3.

**Backfill** — B1 (noya, runtime_confirmed/high, duplicate_known H-03) + B5 (blackhole, runtime_confirmed/high,
duplicate_known M-04); 9 others not_run/none.

**Integrity** — prompt metrics value-for-value unchanged (test + live baseline); panel supplemental-only;
no production source changed; routing_allowed/submission_ready forced false on all rows; un-wired (grep-clean).

**Tests / integrity** — 20 research tests pass; full suite 1657 passed / 2 pre-existing snapshot fails / 4 skipped;
`bash -n` clean; self-test OK; active `output/` symlink unchanged.

**Decision** — ACCEPT_RUNTIME_PANEL.

**Next recommended phase (P147)** — either (a) take a **non-duplicate** corpus item to a runtime PoC so a row flips
to `runtime_confirmed` *without* `duplicate_known` (a genuinely novel runtime-confirmed advisory the panel can
surface), or (b) extend the panel with a `runtime_refuted`/`partial` example to exercise the full vocab, or
(c) a human reachability/severity review of B5 (analogous to P144).
