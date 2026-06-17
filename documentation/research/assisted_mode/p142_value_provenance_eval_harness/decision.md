# P142 — Decision

## Decision: **ACCEPT_STANDING_HARNESS**

The standing `eval_only_manual_queue` harness works end-to-end (`seed` → `ingest` → `scorecard`), is **research-only
and UN-WIRED** (grep-clean of `run_pipeline.sh` + `agent_policy.json`; four research flags + `routing_allowed:false`
on every output; routed inputs refused), **reproduces the P138/P141 baseline** from real recorded outcomes
(11 items, finding 3 / needs_human 1 / strong_clear 7, useful_recall 0.80, strict 0.60), and shows
**clean_false_finding_rate 0.00**. No production file was modified.

### Rubric
- **ACCEPT_STANDING_HARNESS** ✅: seed/ingest/scorecard work; research-only + un-wired verified; baseline
  reproduced; 0 clean false findings; idempotent + time-series.
- Not ACCEPT_RESEARCH_ONLY_LIMITED: coverage is the full 11-item corpus across 3 architectures and the baseline
  matches exactly.
- Not TUNE_AND_RETEST: schema/commands/tests are stable (14 passed); nothing fragile.
- Not REJECT_OR_DEFAULT_OFF: nothing routes/confirms/submits; no production state touched.

## Final response

**What the harness is** — a reusable research-only instrument: corpus registry (`corpus.jsonl`) →
`value_provenance_eval_harness.py` (seed/ingest/scorecard) → research workspace scorecard + time-series. Invariant
"Aggregate, don't adjudicate."

**Reuse** — imports the unchanged P140 `ingest_results()` safety merge; adds zero production lines; un-wired.

**Corpus** — 11 real recorded P137/P138/P141 blind outcomes with provenance; provenance-less rows refused (no
fabrication).

**Scorecard (baseline)** — finding 3 / needs_human 1 / strong_clear 7 / error 0; useful_recall 0.80; strict 0.60;
**clean_false_finding_rate 0.00**; per-arch noya/blackhole/size; `runs[]` time-series.

**Safety** — research-only (4 flags + routing_allowed:false), un-wired, fail-open, idempotent, writes only under
`data/research/` + `output_research/`, no audit touched.

**Tests / integrity** — 14 new pass; full suite 1651 passed (1637 baseline + 14) / 2 pre-existing snapshot fails /
4 skipped; `bash -n` clean; self-test OK; `output/` symlink + `agent_policy.json` unchanged.

**Decision** — ACCEPT_STANDING_HARNESS.

**Next recommended phase (P143)** — either (a) grow the corpus with new neutral packets + operator-run blind
deep-passes across a 4th architecture and watch the time-series for clean-FP drift, or (b) advance one corpus
`finding` (B1/B5) to a Level-3 runtime PoC harness — converting one prompt-derived advisory into a
runtime-confirmed result — while keeping prompt-derived and runtime-confirmed strictly separate (the harness would
then record both a `prompt_decision` and a separate `runtime_status`).
