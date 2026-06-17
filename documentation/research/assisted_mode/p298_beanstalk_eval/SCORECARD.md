# P298 — SCORECARD (beanstalk-2024-05)

Eval of the EXISTING 44 merged findings with the current stack. Answer key read-only; discovery pre-existing.

## Axis 1 — Answer key (recall/precision)
- answer_key_size **81 public** · HIT 15 / PARTIAL 19 / ADJACENT 9 / MISS 38
- **recall_useful = 0.42** (HIT+PARTIAL / 81) · recall_any_touch = 0.531
- **platform_confirmed accepted = 12** · pipeline_only_unmatched = 8 (precision context)

## Axis 2 — Novelty (KB cosine sim, 51k solodit; novel < 0.4)
- **0 novel / 44 known** (all 44 map to a known pattern class; sim range ~0.50–0.79)
- immunefi MCP corroborates the confirmed loci's classes as known/awarded (see immunefi_crossref.json)

## Axis 3 — Validity (executed-PoC; verifier is sole judge; confirmed = executed PASS only)
- targets **12** (the 12 accepted) · **confirmed_by_execution 2** (AC-001, AC-003) · **confirmed_FP 0**

| id | sev | build | verifier verdict | attacker_verified | agent_claimed |
|---|---|---|---|---|---|
| LG-001 | | poc | setup_only | False | confirmed |
| AC-001 | | poc | confirmed_by_execution | True | confirmed |
| AC-003 | | poc | confirmed_by_execution | True | confirmed |
| PC-001 | | poc | setup_only | False | confirmed |
| SN-001 | | poc | setup_only | False | confirmed |
| US-001 | | bundle | needs_execution | False | - |
| BSA-001 | | bundle | needs_execution | False | - |
| BSA-003 | | bundle | needs_execution | False | - |
| EA-001 | | bundle | needs_execution | False | - |
| FL-001 | | bundle | needs_execution | False | - |
| CC-002 | | bundle | needs_execution | False | - |
| DS-003 | | bundle | needs_execution | False | - |

### Validity breakdown (honest)
- **2 confirmed-by-execution** (attacker-exploit): AC-001 (migration signature replay → double credit), AC-003 (unguarded UnwrapAndSendETH sweeps WETH to caller-supplied recipient). Real forge exploit PASS + L1+L2+L3 + assertion_map.
- **3 setup_only** (LOGIC/CORRECTNESS bugs proven by a passing differential test, but the verifier's exploit-shaped L1 'attacker entry' is N/A): LG-001 (ReseedField inner loop `for(uint j;...;i++)` — verbatim source bug, the migration reverts/bricks), PC-001 (totalDeltaB returns one well not the sum), SN-001 (Flood plenty live-roots over stale rain.roots divisor). Builders claimed confirmed; the verifier (sole judge) did NOT confirm → judge-not-builder guard.
- **7 needs_execution** (evidence-bundle, too entangled to mock faithfully): US-001/BSA-001/BSA-003 (reseed init/order), EA-001/FL-001 (sandwich/flash), CC-002 (cross-chain), DS-003 (OOG).

## Headline
The current stack on a real answer key: **recall 34/81≈42% useful (12 platform-confirmed); 0/44 novel (all known classes); validity 2 awarded loci PROVEN by executed PoC at confirmed-FP=0**, 3 logic-bugs proven-by-test-but-setup_only, 7 evidence-bundled. The verifier confirms attacker-exploit bugs but under-credits logic/correctness bugs — the clear next improvement (a logic-bug validity mode).
