# P278 — EXPANDED_REPLAY_RESULTS

Corpus = 12 eval audits (P276 set). `p277_corpus_replay` (body signals on) at handoff budget {5,8,10}, max_classes=8;
funnel-mapped + metrics via the frozen p276 scripts.

## Budget ablation (class_routed % on the 144 locus-mapped awarded H/M)
| handoff budget | class_routed % | mechanism_generated % | missed % |
|---|---|---|---|
| 5 (P277 landed) | 41.7 | 41.7 | 31.9 |
| 8 | **53.5** | 52.8 | 31.9 |
| 10 (landed) | **53.5** | 52.1 | 31.9 |

- **+11.8pp class_routed** (41.7 -> 53.5), clearing the >=50% intent. Saturates at budget 8 (budget 10 = same; most
  contests have <8 routable handoff candidates). `missed` is unchanged 31.9% — those are RECALL/MANIFEST gaps
  (unsurfaced loci) a budget/handoff change cannot touch.
- Attribution recap: P277 showed body signals = +2.1pp; this phase shows the **handoff budget is the dominant lever**
  (+11.8pp). Both land together (body + budget 10).

## Validation queue (budget 10)
queue sizes [4,4,6,6,7,7,7,8,8,8,9,10], avg **7.0**; reaches 10 (revert-lend); classes/contest avg **4.2**.
Anti-monoculture(40%) satisfied **11/12** contests — only quantamm (queue=4, 3 classes) trips it (a small-queue
artifact: 4 candidates can't keep a class <40% while also covering >=3 classes). severe concluded/reportable **FP = 0**.

## Readiness (corpus auto + hand sample)
auto-extracted across 12 contests: **84 candidates, all NEEDS_MORE_EVIDENCE**; hand-authored sample: **2
READY_FOR_POC_INTENT**. operator burden ~7 candidates/contest to validate (PoC capped at 5).
