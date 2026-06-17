# P301 — RESULTS (iteration-1 validation of the standing /loop)

- 20-target queue built; **3 targets scored** this iteration.
- **recall gap mined: 58 missed/under-recalled awarded findings** (staged to data/learning/_proposed/recall_gap_backlog.jsonl, promoted=false).
- **recovered via executed PoC: 2** (panoptic M-01, silo M-06) — confirmed-FP=0, submission-filter 0 leaks.

## Per target (this iteration)
| target | key_source | status | recall gap (missed/under) | recovered |
|---|---|---|---|---|
| revert-lend-2024-03-strict-eval | match_matrix | scored | 31 (27/4) | - |
| panoptic-2025-12-strict-eval | match_matrix | recovered | 22 (19/3) | ['M-01'] |
| silo-finance-2025-03-strict-eval | match_matrix | recovered | 5 (1/4) | ['M-06'] |

## Reading
- The match_matrix MISS/ADJACENT/PARTIAL rows ARE the pipeline's missed/under-recalled awarded findings — mined directly (revert-lend 31, panoptic 22, silo 5 = 58). These are the recall-gap backlog.
- Recovery is gated by the executed-PoC verifier: panoptic M-01 (rounding-direction, logic_differential) and silo M-06 (fee-share rounding, logic_differential) recovered to full executed confirmations at confirmed-FP=0; the rest are needs_execution (PoCs to build over subsequent /loop iterations).
- The loop is resumable (loop_state.json) and self-paces via ScheduleWakeup. The remaining 17 targets + the un-recovered gap are processed across iterations; run `/loop` to continue.

## Cumulative
Executed-confirmed across the program: 23 (through P300) + 2 recall recoveries (panoptic M-01, silo M-06 — already counted in P300; here re-confirmed via the loop path). The NET-NEW value is the 58-item recall-gap backlog now standing + the repeatable loop.
