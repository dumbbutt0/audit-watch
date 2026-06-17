# P276 — FALSE_POSITIVE_REPORT

## Severe concluded/reportable FP: **0**
By construction: the P276 run exercises only the **upstream advisory funnel** (harness → coverage → triage). Nothing is
concluded, reported, given severity, or marked submission-ready/confirmed — all artifacts carry `emits_findings:false`
and advisory status. The strict late gate (exact mechanism + attacker path + delta + victim/gainer + runtime + FP
refutation) is **not reached** in this mapping phase, so no candidate can become a severe FP.

## Advisory-only non-awarded survivors (PoC-queue noise pressure)
Triage-selected candidates that did **not** match any awarded finding = **43** across the corpus. These are
advisory-only (they would enter a PoC queue, never a report). This is the upstream-recall/precision trade the user
endorsed: widen early, keep the late gate strict. Per-corpus detail in `outputs/corpus_metrics.json`
(`false_positive_report.by_corpus`).

## Taxonomy of non-awarded survivors
Not individually adjudicated in this mapping phase (would require completion/PoC on each, the sampled tail). Recorded
as `advisory_only_nonawarded_survivors`; the blind sample (P274/P275) showed such survivors resolve to
BENIGN / NONAWARDED_TRUE_POSITIVE / SAME_AREA_WRONG_MECHANISM at completion — **0 became severe concluded/reportable
FP** there too.

## Conclusion
Recall was raised/measured upstream while the severe-FP count stayed **0** — the intended "high recall upstream, low FP
downstream" posture holds.
