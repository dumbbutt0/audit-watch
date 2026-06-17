# P253 — Phase: Chain-Completion Forensics (the 5-step table)

For each finding where a candidate/observation existed and the award exists but the **exploit chain was never
completed**: (1) candidate that existed, (2) question that was answered, (3) the award's chain, (4) the FIRST
missing reasoning step, (5) the reusable operation it maps to. Operations:
ADVERSARIAL_ACTOR_SUBSTITUTION (AAS) · STATE_TRANSITION_SIMULATION (STS) · CROSS_CALL_IDENTITY_TRACKING (CCIT)
· TERMINAL_STATE_EVALUATION (TSE) · INVARIANT_DELTA_COMPUTATION (IDC) · UNKNOWN. One per finding (earliest
missing step). Ground truth: salty from the StakingRewards/DAO source (read P252) + revealed award summaries;
the rest from the P247/P248 revealed keys. **Read-only; missing steps reconstructed against known ground
truth (caveat in VERDICT).**

## Primary — P252 checkpoint-hit-but-MISSED (salty; checkpoint fired on the exact locus, recall still 0)
| Award | Sev | Candidate that existed | Question answered | Award chain | First missing step | Op |
|---|---|---|---|---|---|---|
| H-02 | High | accounting checkpoint fired A1/A3 on `_increaseUserShare`; flagged rounding | "rounding favors protocol; conserved" | first staker into a pool (`existingTotalShares==0`) skips the virtualRewards branch → later rewards make their `userRewardForPool` disproportionate → first LP drains bootstrapping rewards | never **simulated the empty-pool / first-actor state** (the `existingTotalShares==0` branch) | **STS** |
| H-04 | High | same locus `_increaseUserShare` observed | "virtualRewards keeps ratio" | adversarial first-deposit sequence from the empty state corrupts virtualRewards accounting | never **simulated the adversarial first-deposit sequence** from empty state | **STS** |
| M-01 | Med | accounting fired A1/A3 on `_decreaseUserShare`; flagged rounding as "protocol-favorable dust" (SA-5) | "rounding is protocol-favorable, user dust" | an attacker **chooses** `decreaseShareAmount` so `virtualRewardsToRemove` rounds to 0 → claimable = full rewardsForAmount → repeat → drain | never **substituted an adversary who chooses the input** to control the rounding direction | **AAS** |

## Corroborating — P248 NO_EXPLOIT_CHAIN_CONSTRUCTION (born-but-incomplete, multi-contest)
| Award | Candidate that existed | First missing step | Op |
|---|---|---|---|
| decent H-03 | refund-on-failure path flagged (D-M2) | trace `from` across UTB→adapter→router→executor → it is the wrong address | **CCIT** |
| decent H-04 | reserve check flagged (off-by-one) | follow the `reserves < amount` branch to its terminal state → user holds unbacked dcntEth, lost ETH | **TSE** |
| vultisig H-02 | whitelist-on-recipient noted | substitute a non-whitelisted attacker as the actor | **AAS** |
| vultisig M-03 | examined maxCapPerUser/buy | simulate transferring the NFT then re-buying (ownership transition) | **STS** |
| kleidi M-02 | calldata-index fragility flagged | compute the exact length boundary (`end−start` vs `+1`, full-width param) | **IDC** |
| centrifuge M-04 | deposit/mint callable-for-others noted | substitute an attacker depositing dust FOR a victim | **AAS** |
| centrifuge M-05 | orderbook/escrow accounting flagged | evaluate the shared-escrow terminal state after one user draws it down → others can't claim | **TSE** |
| centrifuge M-07 | rounding-drift flagged | compute the EIP4626 rounding-direction value delta vs the vault (withdraw must round up) | **IDC** |
| munchables H-01 | read lockOnBehalf/_lock | substitute an attacker calling on-behalf for a victim (who-can-trigger) | **AAS** |
| munchables M-03 | remainder-reset flagged (loss direction) | simulate repeated locks accumulating remainder → extra NFTs | **STS** |

## First-missing-step tally (13 findings; weights H=3/M=1)
| Operation | count | weighted |
|---|---|---|
| ADVERSARIAL_ACTOR_SUBSTITUTION (AAS) | 4 | 6 (vultisig H-02 ·3 + 3 Med) |
| STATE_TRANSITION_SIMULATION (STS) | 4 | 8 (salty H-02,H-04 ·3 each + 2 Med) |
| TERMINAL_STATE_EVALUATION (TSE) | 2 | 4 (decent H-04 ·3 + 1 Med) |
| INVARIANT_DELTA_COMPUTATION (IDC) | 2 | 2 |
| CROSS_CALL_IDENTITY_TRACKING (CCIT) | 1 | 3 (decent H-03) |
| UNKNOWN | 0 | 0 |
| **Total** | **13** | **23** |
