# P299 — RESULTS

- logic loci confirmed via differential: **LG-001, PC-001, SN-001** (3/3) · confirmed-FP **0**
- exploit track byte-for-behavior unchanged: **True** (all 7 prior PoCs identical)
- beanstalk validity: **5 confirmed** = 2 exploit (AC-001, AC-003) + 3 logic (LG-001, PC-001, SN-001)
- **cumulative recall-of-confirmed: 15 (arc thru P297) + 5 (beanstalk) = 20 loci**

## Logic confirmations (verifier = sole judge)

- **LG-001** confirmed_by_logic_differential (validity_confirmed=True, attacker=False)
- **PC-001** confirmed_by_logic_differential (validity_confirmed=True, attacker=False)
- **SN-001** confirmed_by_logic_differential (validity_confirmed=True, attacker=False)

## Exploit track (must be identical to pre-P299)

| poc | status | attacker_verified | unchanged |
|---|---|---|---|
| pocs/p286 | confirmed_by_execution | True | True |
| pocs/p294/salty_increaseUserShare | confirmed_by_execution | True | True |
| pocs/p287/kelp/getRsETHAmountToMint | confirmed_by_execution | True | True |
| pocs/p281 | confirmed_by_execution | True | True |
| pocs/p298/beanstalk__AC-001 | confirmed_by_execution | True | True |
| pocs/p298/beanstalk__AC-003 | confirmed_by_execution | True | True |
| pocs/p290/salty-2024-01-holdout/Pools_deposit | refuted_by_execution | False | True |

## Reading
The logic_differential mode confirms all 3 beanstalk logic/correctness awarded loci (LG-001 ReseedField loop off-by-var bricks migration; PC-001 totalDeltaB sums one well not all; SN-001 flood live-roots over stale divisor) by a passing bug-vs-corrected-control differential — no attacker entry. The exploit track is byte-for-behavior identical (all 7 prior PoCs unchanged). confirmed-FP=0; the negative guards (no passing control / failing bug test / no assertion_map) are proven in test_p299. P298's snapshot is preserved (still 2 exploit confirms).
