# P265 — SETUP (Shadow-Mode Operational Trial)

**RESEARCH-ONLY · DEFAULT-OFF · UN-WIRED · MEASUREMENT-ONLY.** P265 is an *operational trial*, not a build and not
a tuning pass. It runs the frozen P264 recall-first shadow harness across 13 real audits, measures 8 metrics, and
decides per the operator's tree. No production edit, no harness/module/config change, no promotion, no wiring.

## What is being trialed
`scripts/research/recall_first_harness.py --mode shadow` (P264), which composes the frozen P260 locus-shape
prioritizer + P262 recall-first shape sweep and emits **advisory-only** recall candidates (status
`ADVISORY_RECALL_CANDIDATE`; severity null; all promotion flags false; 0 concluded/reportable FP by construction).

## Frozen inputs (verified unchanged pre-trial — no tuning)
| artifact | sha256[:16] |
|---|---|
| recall_first_harness.py | `85f9cbe662d2d991` |
| research_recall_first_harness.json | `e9b74687793fd110` |
| recall_first_shape_sweep.py (P262) | `a48336275cb65a4f` |
| research_recall_first_shape_sweep.json (P262) | `62e860199e7c51cd` |
| locus_shape_prioritizer.py (P260) | `d6b494bc3c0cc746` |
| research_locus_shape_prioritizer.json (P260) | `c61da091ad3ed21e` |
| recall_first_advisory.schema.json | `1b122d842588e671` |

The aggregator records the module/config hashes inside every per-contest `recall_metrics.json`;
`frozen_inputs_identical_across_runs=true` confirms all 13 ran on the same frozen set.

## Trial set (13 real audits) and honest scored-status
Inputs (coverage manifest + accounting checkpoint + state-transition checkpoint) were already frozen in P254–P263
deliverable dirs / `audits/<id>/output/`. **No source / findings / manifest was mutated for this trial.**

| contest | scored-status | note |
|---|---|---|
| benddao | **clean_public_anchor** | P263 public findings; training-confound accepted; the one clean scored anchor |
| concrete | unscored_private_findings | P256: report 404 + private findings repo |
| monetrix | unscored_private_findings | P261: findings repo private |
| reserve | scored_contaminated_leaked | P257: reveal precheck leaked award titles |
| loopfi, basin, bakerfi, plaza, notional, astaria, ethos, hybra, sentiment | scored_contaminated_retrospective | awards seen in P254–259 reveals/training → scored metrics optimistic/retrospective |

**Validity split (decisive for reading the results):**
- **Deterministic / operational metrics — valid across all 13** (no award knowledge used): #1 candidates/audit,
  #6 concluded/reportable FP, #8 recall-delta-vs-narrow-baseline, plus the #2/#7 operator-triage *proxy*.
- **Scored metrics — retrospective/contaminated except benddao**: #3 B/C top-2 reach, #4 PARTIAL/COMPLETED,
  #5 exact-mechanism. Reported separately; benddao is the clean anchor; reveal records used ONLY for retrospective
  scoring, never to generate candidates.

## Hard constraints (held throughout)
- No build / tuning / promotion / wiring. Harness + P260 + P262 + configs byte-identical (verified pre/post).
- Candidates ADVISORY only; guard PASS (0 violations) on every contest; FP#6 = 0.
- No answer-key use to GENERATE candidates. Forbidden files byte-identical. Active audit `size-credit-2024-06-blind`
  unchanged (no `switch_audit`).
