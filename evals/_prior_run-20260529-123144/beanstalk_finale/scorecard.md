# Scorecard — Beanstalk Finale (STRICT scoring)

Total public findings: 81
Exact HIT: 23
PARTIAL HIT: 22
ADJACENT: 9
MISS: 27
Pipeline-only FP: ≈36 (Class A–E; 0 hallucinations)
Overall exact hit rate: 23/81 = 28%
Overall useful detection rate (HIT + PARTIAL HIT): 45/81 = 55%
Worst category: Tractor (0/2 meaningful)
Best category: Silo/Convert (3/3 meaningful)
Most common miss reason: Missed accounting invariant
Most wasteful FP source: attacker_mindset hypotheses leaked into the findings corpus (22 items)

## 1–3 Hit rate overall / by severity / by category

| Severity | Total | HIT | PARTIAL | ADJ | MISS | Meaningful |
|---|---|---|---|---|---|---|
| High | 21 | 9 | 7 | 2 | 3 | 16 (76%) |
| Medium | 31 | 7 | 11 | 2 | 11 | 18 (58%) |
| Low | 29 | 7 | 4 | 5 | 13 | 11 (37%) |

| Category | Total | HIT | PARTIAL | ADJ | MISS | Meaningful |
|---|---|---|---|---|---|---|
| Silo/Convert | 3 | 1 | 2 | 0 | 0 | 3 (100%) |
| Silo/Floods | 6 | 0 | 6 | 0 | 0 | 6 (100%) |
| L2 Migration/Barn | 2 | 0 | 2 | 0 | 0 | 2 (100%) |
| Barn/ERC1155 | 1 | 1 | 0 | 0 | 0 | 1 (100%) |
| Tractor/Pipeline | 1 | 0 | 1 | 0 | 0 | 1 (100%) |
| L2 Migration | 33 | 13 | 9 | 3 | 8 | 22 (66%) |
| Oracle | 9 | 3 | 2 | 2 | 2 | 5 (55%) |
| Auth/Permit | 4 | 2 | 0 | 0 | 2 | 2 (50%) |
| Oracle/L2 | 2 | 1 | 0 | 0 | 1 | 1 (50%) |
| Field/Plots | 4 | 1 | 0 | 3 | 0 | 1 (25%) |
| Protocol Integrity | 5 | 1 | 0 | 0 | 4 | 1 (20%) |
| Tractor | 2 | 0 | 0 | 0 | 2 | 0 (0%) |
| Oracle/Barn | 1 | 0 | 0 | 0 | 1 | 0 (0%) |
| Silo/Rewards | 1 | 0 | 0 | 0 | 1 | 0 (0%) |
| Silo/Stalk | 3 | 0 | 0 | 0 | 3 | 0 (0%) |
| Pipeline/Tractor | 1 | 0 | 0 | 0 | 1 | 0 (0%) |
| Silo/Whitelist | 1 | 0 | 0 | 1 | 0 | 0 (0%) |
| Auth/Events | 1 | 0 | 0 | 0 | 1 | 0 (0%) |
| Protocol Integrity/Oracle | 1 | 0 | 0 | 0 | 1 | 0 (0%) |

## 4–12 Other scorecards

- Partial-hit rate: 22/81 = 27%
- Adjacent rate: 9/81 = 11%
- Miss rate: 27/81 = 33%
- False-positive count: ≈36 (Class A–E); **0 hallucinations** (every unmatched finding is real code)
- False-positive rate (noise / total emitted ≈ 44 corpus + 36 noise): qualitative — ~45% of the emitted *count* was attacker-mindset hypotheses; genuinely-wrong exploitable claims ≈ 0.
- PoC success rate: 0/0 — **no PoCs were generated** for this target (validation half didn't run; no API).
- Severity accuracy: of 45 matched, pipeline severity resolvable for 36; exact match 11. Mismatches skew to pipeline rating HIGHER than CodeHawks' aggressive downgrades.
- Duplicate-clustering accuracy: 1 known wrongful collapse (OR-001/OR-002, distinct oracle bugs merged); otherwise dedup linked rather than dropped. Five-axis dedup fix is staged.
- Agent/stage contribution (HIT+PARTIAL by agent): behavioral_state_analysis:9, token_integration:5, snapshot:5, upgrade_storage:5, cross_chain:4, oracle:3, logic:3, access_control:2, flash_loan:2, dos:2, arithmetic:2, economic_attack:2, protocol_context:1

_Note: by-severity uses fetched per-finding severities (21H/31M/29L); official aggregate 22/31/28 (one-finding submission-page artifact)._
