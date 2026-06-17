# P135 — Decision

## Decision: **ACCEPT_ADVISORY_SURFACING**

The new surfacing layer routes existing mechanism-detector output into review as **advisory_only** context:
**all 3 P133 MISS** and **all 3 P133 PARTIAL** (and the HIT) reach the standard review surface at production
default, the H-03 residual gets a `deep_pass_value_provenance` recommendation, and **0 entries** are
submission-ready/confirmed/severity-bearing in either mode. Tests pass; caps + config gates present; fully
reversible.

### Rubric
- **ACCEPT_ADVISORY_SURFACING** ✅ — P133 MISS/PARTIAL reach review, no unsafe promotion, 13 tests pass,
  caps/config present.
- Not ACCEPT_EVAL_ONLY: the **production-default** path already recovers all 3 MISS via advisory+report detectors
  (units/CPA/AC); research-only (STC/RPL) is appropriately eval-gated by design — a safe default, not a forced
  eval restriction.
- Not TUNE_AND_RETEST: confidence-prioritized caps keep volume bounded (26 at prod default) and statuses are
  explicit; no noise/label problem.
- Not REJECT_OR_DEFAULT_OFF: advisory evidence is structurally isolated and cannot be mistaken for confirmed.

## Final response

**What changed** — new `scripts/surface_mechanism_advisories.py` (advisory routing layer) + `mechanism_advisory`
config block + 13 tests. Surfaces existing detector output to `output/mechanism_advisory_context.json` and
(gated) `human_review_queue.jsonl` as advisory_only review_context; adds H-03-class `deep_pass_value_provenance`
recommendations.

**What stayed unchanged** — all detectors, severity, submission, gates, and P130–P134 behavior. No detection
logic touched. research_only/report_only status preserved.

**Advisory evidence surfaced** — prod default 26 (CPA 7, AC 9, units 10; 0 research-only); eval 39 (+STC 10,
RPL 3); master-off 0.

**P133 MISS/PARTIAL routing** — all 3 MISS reach review at production default (H-01 units, H-13 CPA, H-14
units+AC); all 3 PARTIAL too (H-06 CPA+AC, H-22 units+AC, H-15 AC); HIT H-19 via CPA. Bonus H-23/H-18 via RPL in
eval.

**H-03 deep-pass routing** — `NoyaValueOracle._getValue` receives a `deep_pass_value_provenance` recommendation
(review_context, no finding/severity), via a general oracle/value-loop heuristic.

**Safety** — 0 unsafe entries (prod + eval); routing_allowed:false; all advisory_only + requires_human_review;
no severity; research/report status preserved; submission gates untouched; master + per-status + caps disable.

**Tests** — 13 new pass; full suite 1599 passed / 2 pre-existing snapshot fails / 4 skipped.

**Integrity** — no detector/severity/submission logic changed; noya queue restored to P133 baseline; self-test
OK; active audit restored to `quantamm-2024-12-eval`.

**Decision** — ACCEPT_ADVISORY_SURFACING.

**Next recommended phase (P136)** — (a) wire `surface_mechanism_advisories.py` into the api-free pipeline at the
review-gate step (run after detectors, before the human pause) so advisories appear automatically, plus a small
**review_gate.md "Advisory Context — NOT confirmed" section** and a dashboard advisory panel; (b) run the
`deep_pass_value_provenance` prompt on the H-03 recommendations to test whether the trace converts the residual
to a confirmed mechanism; (c) advance `semantic_tvl_completeness` toward the 5-criteria research→advisory bar.
