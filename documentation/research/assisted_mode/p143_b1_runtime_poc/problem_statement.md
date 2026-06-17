# P143 — Problem Statement

P137–P142 produced **prompt-derived** advisory evidence for the value-provenance family and built a standing
research harness; the P142 scorecard had **runtime-confirmed = 0**. P142 recommended advancing one corpus
`finding` to a **Level-3 runtime PoC** while keeping prompt-derived and runtime-confirmed status strictly separate.

**P143 does that for B1 — `NoyaValueOracle._getValue`** (the multi-hop oracle/value-loop variable provenance
mechanism).

## Prompt-derived mechanism (from P137/P138, unchanged)
Inside the multi-hop valuation loop the function advances `quotingToken = sources[i]` but calls
`_getValue(asset, sources[i], initialValue)` using the **static original `asset`** instead of the loop-carried
`quotingToken`. So routes with **≥2 sources** mis-value amounts when the per-hop oracle paths differ.

## Primary question
Can a controlled multi-hop route produce a **different output** when the loop uses the static `asset` versus the
loop-carried `quotingToken`, proving the prompt-derived mechanism **at runtime**?

## Answer
**Yes — RUNTIME_CONFIRMED.** The real `NoyaValueOracle` contract, deployed locally and driven through its real
public `getValue` entrypoint, returns **20e18** for a 2-hop route whose corrected (loop-carried) value is
**6e18** — a 3.33× over-valuation. Single-hop and equal-per-hop-price controls show **no** divergence, isolating
the cause to the static-`asset` hop at loop iteration i≥1.

## Strict separation (constraint 9/10)
This runtime result is recorded as a **separate `runtime_status` = runtime_confirmed** field; the
`prompt_decision = finding` / `prompt_status = completed` fields are untouched. Runtime confirmation strengthens
the advisory but does **not** make the finding submission-ready; human review + scope/duplicate/severity checks
remain mandatory.
