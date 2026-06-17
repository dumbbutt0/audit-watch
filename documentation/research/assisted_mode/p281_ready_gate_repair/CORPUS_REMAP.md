# P281 — CORPUS_REMAP (P278 queue through the repaired gate)

`outputs/before_after_ready_queue.json`. 84 validation-queue candidates across 12 contests.

## READY before vs after
| | P279/P280 | P281 |
|---|---|---|
| READY_FOR_POC_INTENT | 3 | **1** |
| PoC-supported among READY | 0/3 | **1/1** |
| severe concluded/reportable FP | 0 | 0 |

## P281 status distribution (after)
READY_FOR_POC_INTENT 1 · INLINE_GUARD_REFUTED 17 · NEEDS_STATE_MACHINE_EVIDENCE 11 · NEEDS_VALUE_FLOW_EVIDENCE 11 ·
NEEDS_SOURCE_SPAN 1 · NEEDS_MORE_EVIDENCE 43.

## Reading
- **Precision up, recall down (intended):** 40 candidates now carry a specific source-span-backed block reason instead
  of a permissive READY/NEEDS_MORE. 17 were inline-guarded (the dominant P280 failure mode), 11 need state evidence,
  11 need value-flow, 1 is an interface decl.
- The single survivor (L2Governor.execute) is a real, source-backed state-machine anomaly that the PoC supports — so
  the READY precision proxy goes 0/3 → 1/1.
- The gate did NOT over-block a known-good candidate (the only PoC-supported mechanism we have, the state-machine one,
  passed) — so this is not "too strict."
