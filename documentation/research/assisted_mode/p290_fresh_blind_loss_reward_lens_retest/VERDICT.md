# P290 — VERDICT

## Verdict: **D — READY_GENERATED_BUT_NOT_SUPPORTED**
## Bottleneck: **F — EVIDENCE_DERIVATION_GAP**

## Core question
Do the frozen post-P289 lenses (and the full stack) produce a high-quality READY/PoC-supported candidate on a fresh
target before reveal, without false READY? **Answer for salty: no.** The stack produced **1 READY (`Pools.deposit`)** but
its claimed EXTERNAL_INTEGRATION callback mechanism was **PoC-REFUTED pre-reveal** (the function is `nonReentrant` with a
plain `safeTransferFrom`); **0 P289 lens firings**; **0 awarded mechanism recovery**.

## Why D
- D = "READY appears but PoC unsupported/refuted." Exactly: 1 READY, PoC PASS_REFUTED → PRE_REVEAL_READY_UNSUPPORTED.
- Not A/B (0 awarded exact/strong recovery; no lens fired). Not C (no PoC-supported non-awarded TP — the candidate was
  refuted). Not E (a READY did appear). Not F-verdict/G (no safety/contamination breach).

## Honest findings
1. **The P289 lenses did NOT generalize to salty (0 firings)** — even though salty's marquee awarded Highs (H-02/H-04)
   are reward-index/first-depositor bugs, exactly Lens 3's class. The lens was **starved by recall**: the awarded
   internal locus `StakingRewards._increaseUserShare` was never surfaced (only `claimAllRewards` was queued).
2. **The one READY was a READY-layer false positive** from the pre-existing P279 EXTERNAL_INTEGRATION template (lifts on
   class label + a generic callback hypothesis, invariant_delta NO_REFERENCE). It was caught pre-reveal by its own PoC →
   never concluded/reportable (severe FP=0), but it is a precision regression vs P289's clean 0-false-READY corpus run.

## Integrity
severe concluded/reportable FP = 0 · 0 fabricated passes · frozen stack unchanged (0 mismatches; deriver/config/etc.
byte-identical) · active audit unchanged · salty contest source unmutated · production authority WITHHELD.

## Decision-tree consequence
P290 is **not A/B/C** → **do NOT move to scaleout.** Two precise next repairs (then re-blind), neither recall-scaleout:
1. **EXTERNAL_INTEGRATION READY precision**: require a source-backed deviation (e.g. an actual external callback / missing
   reentrancy guard / fee-on-transfer accounting) before lifting; do not lift on the class template + a generic callback
   hypothesis. (Fixes the unsupported-READY / false-positive.)
2. **Recall for internal accounting loci** (`_increaseUserShare`-style internal share/reward functions) so the
   reward-index lens (Lens 3) actually gets a candidate to fire on.

## Next
Repair the two localized gaps above (supervised, on this evidence), then **re-blind a fourth target** before any scaleout.
