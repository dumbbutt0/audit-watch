# P270 — VERDICT

## Bottleneck: F — POC_HARNESS_GAP
## Verdict: C — STRONG_PARTIAL_ONLY_NEEDS_COMPLETION_REFINEMENT

### Why
On a fresh, zero-exposure external contest (wise-lending, 2024-02), with BOTH selection fixes enabled, the full path
behaved as the arc predicted — and made a **genuine, first-of-its-kind advance**:
- **The selection layers steered the PoC queue onto the EXACT awarded loci of two awarded Highs.** Recall surfaced
  the award subsystems; the P267 selector preserved the high-impact mechanisms (KEEP_BOTH); the P269 impact-first
  triage routed the heavy award-class subsystems as SELECT_FOR_PARTIAL_RUNTIME — and two of the three routed loci are
  **H-03 (FeeManager bad-debt accounting)** and **H-04 (WiseCore liquidation collateral misallocation)**. The
  P266 ranking-drop and P268 triage-de-scope are **both resolved on fresh data**, and routing now lands on awarded loci.
- **Result: 2 FAMILY_LEVEL_MATCHES** to awarded Highs (C-bd→H-03, C-liq→H-04), **0 exact, 0 strong**, **0 severe
  concluded/reportable FP**. The one harness-feasible PoC (C-pp Pendle-share) correctly **refuted** its (non-awarded)
  mechanism — a true negative, not a false positive.

This is family-level recovery to the right awarded loci without exact confirmation → **C**.

### Why not A / B
A/B require ≥1 EXACT awarded mechanism recovered **with PoC/strong-runtime support**. Result: 0 exact, 0 strong; the
two awarded-locus candidates were FAMILY-level (hypotheses didn't pin H-04's private-vs-public collateral split or
H-03's partial-liquidation global-vs-position deduction) and their confirming PoCs were **not built** (NEEDS_MORE_
RUNTIME — full WiseLending deposit→borrow→liquidate→bad-debt stack is harness-heavy). No hindsight credit taken.

### Why not D / E / G
- Not **D** (still selecting non-awarded true positives while awarded missed): the opposite happened — selection
  routed ONTO the awarded loci; the one non-awarded mechanism (C-pp) was refuted, not PoC'd as a finding.
- Not **E** (signal too thin): the routing-onto-awarded-loci signal is strong and decisive (2 awarded Highs' loci
  routed), not thin — the gap is specifically completion/PoC depth, which **C** names.
- Not **G**: no safety/contamination trip — 0 severe concluded/reportable FP, no award leak before the Phase-9
  freeze, frozen modules + 5 forbidden byte-identical, active audit unchanged, contest source unmutated.

### The arc resolution
P266 RANKING_GAP → P267 fixed · P268 TRIAGE_GAP → P269 fixed · **P270: both selection fixes work on fresh data and
route onto awarded loci** → the binding gap is now **POC_HARNESS_GAP / completion-precision on heavy protocols**:
turning a family-level awarded-locus hit into an exact, PoC-confirmed mechanism. The "selection-upstream" theme
(P259→P268) is closed; the frontier is downstream completion + PoC depth.

### Required next step — P271
Strengthen **completion-precision + PoC-harness depth on heavy protocols**: build full/partial-runtime PoC
scaffolding for lending stacks (deposit→borrow→liquidate→bad-debt) so a routed award-locus candidate can be sharpened
from family-level to exact and PoC-confirmed; re-run on wise-lending's H-03/H-04 loci (now known-routed) and/or a
fresh contest, scoring exact recovery. Production authority remains **withheld**.

### Honest note (the user's framing)
This run did NOT find "non-awarded true positives while missing awarded" (the D failure). It routed onto the awarded
loci and fell short only at exact mechanism confirmation due to PoC-harness weight. That is the cleanest possible
"not-yet-A" outcome: the objective-mismatch worry (real-bug discovery ≠ contest-award matching) did **not** bite —
the system pointed at the awarded bugs; it just couldn't yet prove them exactly on a heavy stack.

### Constraints honored
Research-only / advisory. No frozen-module tuning: P260 `d6b494bc` · P262 `a48336275f` · P264 `85f9cbe6` · P267
`b0623b8c` · P269 `63c88d02` (+ configs) byte-identical pre/post. 5 forbidden byte-identical. Active audit
`size-credit-2024-06-blind` unchanged. wise source isolated in `/tmp` (never under `audits/`); contest source
unmutated; PoCs under `pocs/p270/`. Answer key opened only after the full pre-reveal freeze manifest was hashed.
No answer-key content used to generate candidates or assign selector/triage dimensions.
