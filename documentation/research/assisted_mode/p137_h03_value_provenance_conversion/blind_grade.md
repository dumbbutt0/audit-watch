# P137 — Blind Grade (before answer key)

Graded by me (contaminated) on the genuinely-blind subagent outputs. The PASS was blind; only the grade is informed.

## T1 — H-03 NoyaValueOracle._getValue → **PROMPT_HIT**
- **Mechanism claim:** in-loop hop uses the static `asset` instead of the updated loop-carried `quotingToken`
  → wrong from-token for every hop after the first. Source-cited (`initialValue = _getValue(asset, sources[i],
  initialValue)`).
- **Impact claim:** ≥2-hop routes mis-value the asset (value denominated in sources[i-1] priced via asset→sources[i]).
- **Rejected alternatives:** single-hop correct; distinct oracles ⇒ not equivalent; not a benign view.
- **Confidence:** high (`finding`). **Enter human_review_queue:** yes (advisory_only). **PoC/runtime needed:**
  recommended to confirm the ≥2-hop precondition + oracle distinctness, but the mechanism is source-decisive.
- This is the correct stale/static loop-variable value-provenance mechanism with source evidence → **PROMPT_HIT**.

## Controls (specificity)
- **T4 clean `convertCToL` → strong_clear** (correct; no over-flag).
- **T2 single-hop oracle `getValue` → needs_human** (careful; surfaced a real units concern as uncertain, not a
  false finding).
- **T3 Morpho TVL → finding** (correct sign-error call, but aided by my role annotation — discount as evidence).

## Specificity read
1 strong_clear (clean), 1 needs_human (uncertain), 2 findings (both real awarded bugs). **No PROMPT_FALSE_POSITIVE
on the clean control.** The prompt stayed in its lane and did not invent unsupported claims → not noisy.
