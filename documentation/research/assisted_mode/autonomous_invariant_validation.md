# Autonomous Invariant Validation (P101)

**Status:** RESEARCH-ONLY, advisory, un-wired. Date: 2026-06-03.

## What changed
Earlier assisted mode (P98–P100) paused for a human to **pick** the invariant. P101 removes that pause: the
system **auto-enumerates many candidate invariants and defense maps per surface, then auto-validates them through
the existing reject-first gates**, ranking only PoC-ready candidates for the human. The human no longer selects
which invariant to test — they review the final candidates, confirm/rerun the PoC, do scope/duplicate/program-
severity, and submit manually.

## The three layers (kept strictly separate)
1. **`generated_invariants` — broad recall.** Numerous, `HYPOTHESIS_ONLY`. **These are NOT findings.**
   (`scripts/assisted/enumerate_candidate_invariants.py` — category-complete over 11 invariant types so the
   relevant invariant is always present; this is the direct fix for P97's "tested a true-but-irrelevant
   invariant".)
2. **`validated_candidates` — precision-gated.** Only candidates that survive source trace + defense mapping +
   adversarial ordering + maximal consequence + hygiene + severity gate (`193abf9f`).
3. **`human_actionable_candidates`** — only `VALIDATED_FOR_POC_HANDOFF`, or `NEEDS_EXECUTION` **with an exact test
   idea**.

> **Generated hypotheses are not findings. Rejections are precision wins.** The dashboard/report must never render
> `generated_invariants` as findings.

## Pipeline
`enumerate_candidate_invariants` (recall) → `map_invariant_defenses` (precision aid: COVERS / PARTIALLY_COVERS /
DOES_NOT_COVER / UNKNOWN_NEEDS_TRACE) → `auto_validate_invariants` (reuses the frozen
`validate_candidate_invariant` chain) → rank → `lab_report.md` / `lab_queue.json` / `ranked_candidates.json`.

Per-invariant decisions: `REJECTED_DEFENSE_COVERS` · `REJECTED_SOURCE_PROVEN_SAFE` · `NEEDS_CONTEXT` ·
`NEEDS_EXECUTION` · `VALIDATED_FOR_POC_HANDOFF` · `BLOCKED_UNSUPPORTED_CLAIM`. The loop only pauses for a human
when all candidates are rejected, a candidate needs runtime data, or a candidate reaches PoC handoff.

## Precision is preserved (recall does not bypass precision)
- `HYPOTHESIS_ONLY` candidates cannot enter the funnel as `POC_HANDOFF_STARTED` (the funnel's existing
  `can_promote_to_poc_handoff` requires a real conversion + passed severity gate + adversarial PASS).
- Missing `source_refs`/`source` or `affected_actor` → blocked at `NEEDS_CONTEXT`.
- A defense that **COVERS** the invariant rejects it (`REJECTED_DEFENSE_COVERS`) **unless a concrete bypass /
  counterexample is shown** — recall expansion never silently bypasses a real defense.
- A severity FP → `BLOCKED_UNSUPPORTED_CLAIM`. No candidate becomes submission-ready without a reproduced PoC;
  nothing is ever auto-submitted.

## Honest boundary
- The enumerator is a **deterministic, category-complete heuristic** (keyword/state-var/detector signals), not an
  LLM that "understands" arbitrary code. Its recall value is *never omitting a plausible invariant category*.
- "Autonomous validation" automates **trying every candidate and gate-filtering** — it does not automate the
  underlying code reasoning. Reaching `VALIDATED_FOR_POC_HANDOFF` still requires **source-backed trace evidence**
  per candidate (depth_trace + adversarial ordering + impact).
- **Autonomous blind *discovery* remains paused as a product claim.** Autonomous invariant *validation* (try
  many, gate-filter, surface only PoC-ready) is what is enabled here.

## Tomorrow's hunting workflow
1. Pick target (e.g., K2). 2. Surface/detector pass. 3. For each suspicious function, run
`enumerate_candidate_invariants`. 4. `auto_validate_invariants` maps defenses + validates all candidates (no human
picks). 5. Review `human_actionable_candidates`; confirm/run the PoC. 6. Human does scope/duplicate/severity →
record `APPROVED_TO_SUBMIT`/`DO_NOT_SUBMIT` → manual submit. **Enumerate many invariants; validate only
source-backed ones.**
