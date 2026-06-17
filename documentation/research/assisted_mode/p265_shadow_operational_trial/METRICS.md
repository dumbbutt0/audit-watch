# P265 — METRICS (8 metrics, per-contest + pooled)

Source: `outputs/p265_aggregate_metrics.json` (deterministic from the 13 frozen shadow outputs).
**Validity:** #1/#6/#8 + the #2/#7 proxy are valid across all 13. #3/#4/#5 are retrospective/contaminated except
**benddao** (clean anchor) — see the scored block below.

## Per-contest (deterministic + operator proxy)
| contest | scored-status | #1 cand | #8 recall-Δ | narrow | #2 worth (proxy) | #7 min/lead | #6 FP | guard |
|---|---|---|---|---|---|---|---|---|
| loopfi | retro | 13 | 8 | 5 | 4 (31%) | 13.0 | 0 | PASS |
| basin | retro | 11 | 8 | 3 | 0 (0%) | – | 0 | PASS |
| bakerfi | retro | 17 | 12 | 5 | 2 (12%) | 34.0 | 0 | PASS |
| plaza | retro | 15 | 11 | 4 | 4 (27%) | 15.0 | 0 | PASS |
| concrete | unscored | 14 | 12 | 2 | 7 (50%) | 8.0 | 0 | PASS |
| notional | retro | 16 | 11 | 5 | 9 (56%) | 7.1 | 0 | PASS |
| reserve | leaked | 23 | 18 | 5 | 2 (9%) | 46.0 | 0 | PASS |
| astaria | retro | 14 | 9 | 5 | 7 (50%) | 8.0 | 0 | PASS |
| ethos | retro | 18 | 13 | 5 | 12 (67%) | 6.0 | 0 | PASS |
| hybra | retro | 23 | 18 | 5 | 6 (26%) | 15.3 | 0 | PASS |
| sentiment | retro | 16 | 11 | 5 | 10 (63%) | 6.4 | 0 | PASS |
| **benddao** | **clean** | 17 | 12 | 5 | 4 (24%) | 17.0 | 0 | PASS |
| monetrix | unscored | 19 | 14 | 5 | 5 (26%) | 15.2 | 0 | PASS |

## Pooled (all 13)
- **#1 advisory candidates/audit:** 216 total · **mean 16.6** · range 11–23 (bounded by the cap=25; never floods).
- **#6 severe concluded/reportable FP:** **0** · guard PASS on all 13 · 0 promotion flags set. *(0 concluded/
  reportable FP by construction — NOT a claim of true 0-FP; advisory candidates still require human triage.)*
- **#8 recall-delta:** 157/216 = **72.7%** of advisory candidates are forced in *beyond* the narrow top-5 baseline.
  narrow=59. This is the core "recall lift" signal — the harness's value lives in loci the old narrow path skipped.
- **#2 worth human review (proxy):** 72/216 = **33.3%** (recall-delta ∩ award-class-fit family ∩ checkpoint
  evidence-marker). ~1 in 3 advisory candidates is a genuinely interesting subtle-family recall-delta lead.
- **#7 operator minutes/useful lead (proxy):** **12.0 min** pooled (4 min/candidate triage ÷ 33% useful).

## Scored block (#3/#4/#5) — benddao clean anchor; rest retrospective
**benddao (clean, P263):** 8 Highs.
- **#3 reaching B/C top-2 (correct family):** of the 4 Highs whose loci the harness forces in as recall-delta
  (H-01, H-05, H-06, H-08), all carry a B/C handoff with the award-fit family (H-08→T5, H-05→T7, H-01/H-06→T8/yield);
  the other 4 Highs are out-of-class (H-02/H-03/H-07 access-control, H-04 mechanical-math) and are correctly NOT
  targeted (precision, not miss). So **recall-delta covers 4/4 in-class Highs; 0/4 out-of-class** (by design).
- **#4 reaching PARTIAL/COMPLETED:** the shadow harness does **not** run completion (=0 by design). The P263
  *manual* downstream run reached **1 PARTIAL_CHAIN** (H-08, T5 family-match). No COMPLETED.
- **#5 exact-mechanism:** **0 exact**; **1 family-level** (H-08 T5). This is the decisive limitation → P266.

**Retrospective (contaminated, do NOT pool as a rate):** loopfi High #399 self-liquidation (completed in P254);
basin High #17 + Med (T9 math); bakerfi 0 clean; plaza awarded fee/#756 = B/C runner-up (mis-ranked #1);
notional #886 double-fee B/C-selected; astaria 0 (out-of-class mechanical/access/token); ethos #693 external-AAVE
DoS (T1 family, discovery miss); hybra gHYBR `GrowthHYBR.deposit` T8 (the P259 locus-selection miss the P260
prioritizer fixed — forced in here); sentiment #613 bad-debt share-inflation T8 (right shape). These corroborate
the benddao pattern: **recall-delta reliably forces award-carrying loci in; exact-mechanism/completion is the gap.**
