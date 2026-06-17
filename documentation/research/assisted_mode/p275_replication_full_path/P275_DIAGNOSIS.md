# P275 — DIAGNOSIS (Phase 11)

## Verdict: **F — TARGET_NOT_DIAGNOSTIC**
## Bottleneck: **A — TARGET_FIT_GAP** (secondary: F COMPLETION_GAP on the one downgraded issue)

### Core question and why it can't be answered here
*Can the full path recover ≥1 awarded mechanism (EXACT/STRONG) again on a second fresh diverse target?* — **The target
yielded 0 awarded High/Medium vulnerabilities** (C4 Summary, verbatim). A target with no awarded H/M cannot validate or
refute replication. P275 is therefore **inconclusive as a replication test** — verdict F, not a pass and not a fail of
the pipeline.

### What the Phase-0 screen got right and what it missed
- **Right:** ronin is EVM/Solidity, genuinely multi-class, clean (zero prior exposure), and had a retrievable findings
  repo.
- **Missed (the lesson):** the content-safe screen verified *findings-repo existence* but **not awarded-H/M
  existence**. "A `-findings` repo exists" ≠ "the contest produced awarded High/Medium findings." This contest's
  awards were entirely Low/QA. **Target selection must pre-verify that awarded H/M severity findings exist** (the
  content-light C4 Summary line "yielded N HIGH/MEDIUM" is exactly that signal — readable without opening any finding
  body).

### Distribution
- Awarded H/M issues: **0**. Low/non-critical: 3 reports. One downgraded issue (#32, callback address-collision)
  included by sponsor request.
- Routed classes (my path): STATE, ACCESS, ORDER, SHARE (4). Awarded-class distribution: **N/A** (no awards).
- EXACT/STRONG/FAMILY awarded recoveries: **0 possible** (no awards).
- Non-awarded true positives: 1 (M1 `tx.origin` deviation, real, unexploitable on-chain).
- SAME_AREA_WRONG_MECHANISM: 1 (M2/M3 callback subsystem vs downgraded #32).
- **Severe concluded/reportable FP: 0.**

### Honest secondary finding (COMPLETION_GAP)
Even setting awarding aside, the **one substantive issue (#32, mint-callback address collision)** was in my
recall-surfaced and triage-routed subsystem — and I examined the *identical* `computePoolAddress(...) == msg.sender`
validation in the swap callback and **explicitly judged it correct**. The completion checklist for the ORDER/callback
class did not include the **CREATE2 address-collision / EIP-3607 class** ("is a callback's pool-identity check a
brute-forceable CREATE2 address?"). Adding that check would have flipped M2 from "validation correct" to a real
candidate. This is a concrete, reusable completion-checklist improvement — independent of this target's (non-)awarding.

### Comparison to P274 (replication status)
- **P274 (gondi):** 17 awarded H + 20 awarded M; the path recovered 2 EXACT awarded Highs with PoCs.
- **P275 (ronin):** 0 awarded H/M; replication **could not be measured**. This is a **non-diagnostic** datapoint, not
  a non-replication. The P274 result stands; it is neither confirmed-repeatable nor refuted by P275.

### Pipeline integrity (all stages ran clean, blind, safe)
recall → selector (guard 0) → coverage (4 classes, guard 0) → triage (3 classes, guard 0) → completion → Tier-C PoCs
(4/4 pass) → frozen pre-reveal gate → reveal. No tuning; no answer-key leakage pre-freeze; 0 severe FP. The *machinery*
replicated cleanly on a different architecture (AMM/DEX vs lending); only the *measurement* was impossible.

### Per the user's decision tree
**F → target-selection problem.** Next step is **not** algorithm work and **not** rollout. It is to re-run the
replication on a target with **confirmed awarded H/M findings**, using a screen that checks the C4 Summary's
H/M count (content-light) before committing. Also fold the **CREATE2 callback-collision / EIP-3607** check into the
ORDER/callback completion checklist (a genuine gap this target exposed).

### Production authority
Remains **WITHHELD**. P274's breakthrough is not yet replicated; P275 did not provide the second datapoint (target was
non-diagnostic).
