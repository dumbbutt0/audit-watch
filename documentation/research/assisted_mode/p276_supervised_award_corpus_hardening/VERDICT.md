# P276 — VERDICT

## Verdict: **A — CORPUS_MAP_READY_REPAIR_BACKLOG_CLEAR**

### Why A
- **Multiple contests mapped:** 7 locus-mapped contests (144 awarded H/M) fully funnel-mapped + 2 count-only (105) +
  4 excluded (documented).
- **Every H/M award assigned a funnel stage** and a `first_failed_stage` (locus-mapped set); title-only awards recorded
  `DUPLICATE_OR_REPORT_ONLY_AMBIGUITY`.
- **Corpus metrics produced:** surfaced 68.1% · routed 39.6% · mechanism-generated 39.6% · missed 31.9%
  (`outputs/corpus_metrics.json`).
- **Severe concluded/reportable FP = 0** (upstream-only; strict gate never reached).
- **Repair backlog is general and non-target-specific** (`REPAIR_BACKLOG.md` / `repair_backlog.json`): R1 coverage-class
  routing (41), R2 recall depth (30), R5 PoC-scaffold throughput (57), R3 manifest enumeration (16), R4 oracle/external
  classes (6), R6 key enrichment (105) — every signal is a structural source pattern, no contest/award literals.

### Not B / C / D
- Not **B** (needs more corpus): 7 locus-mapped contests across 6 protocol architectures + 249 machine-readable awarded
  H/M is a sufficient first map; the repair backlog is already clear and prioritized.
- Not **C** (too noisy to harden): severe FP = 0 and only 43 advisory-only survivors — the funnel is measurable and the
  leaks are localized, not drowned in noise.
- Not **D** (aborted): research-only, advisory, un-wired; frozen + forbidden byte-identical; active audit unchanged; all
  outputs labeled SUPERVISED_EVAL; no blind-credit claimed.

### Headline repair map (where awards leak, above the expected completion tail)
**Routing (surfaced→routed) is the binding upstream leak**, then **recall depth**, then **manifest enumeration**;
ORACLE_PRICING (0/4) and EXTERNAL_INTEGRATION (1/2) are the weakest classes. Fixes are low-FP-risk (widen upstream;
keep the late gate strict).

### Next
Repairs land in a separate explicitly-approved phase (frozen-module changes gated there); then resume the cadence
(3–5 supervised : 1 blind). Production authority remains **WITHHELD**.
