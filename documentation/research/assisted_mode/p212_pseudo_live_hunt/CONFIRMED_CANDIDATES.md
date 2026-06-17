# P212 — confirmed candidates (verification)

All severities are THREAT CEILINGS; final severity gated by L3. Sophon = POINTS system (points→future L2 allocation),
so most impacts are points-accounting, not direct token theft.

## Permissionless (credible, need harness for severity)
- **SOPH-01 withdraw omits boostAmount decrement** (sf-02, L730-733). Attacker: any depositor. Loses: protocol points
  fairness / the user's own accounting integrity; user.boostAmount stays after withdraw → phantom reward weight.
  Gains: inflated points vs honest users. Fund theft: NO (withdraw bounded by depositAmount). Intended: no. Needs
  harness to show whether phantom-weight is materially exploitable (drain others' point share) vs benign.
- **SOPH-02 accPointsPerShare 1e18 scaling mismatch** (sf-04, L361-376/430-432). updatePool writes pointReward/lpSupply
  (no extra 1e18); _pendingPoints view applies *1e18…/1e36 → view over-reports unsettled pending; settled accounting
  self-consistent. Impact: points view/accrual accuracy. Needs harness to prove on-chain (settled) divergence.
- **SOPH-03 depositStEth wraps full _amount** (sf-05, L473-481). stETH transferFrom delivers _amount-1/2 wei; wrap of
  full _amount → revert (DoS) or consume residual/other-user stETH. Conditional. Needs harness w/ faithful stETH mock.
- **SOPH-04 boost inflates reward denominator** (sf-01/03). pool.amount synthetic inflation dilutes honest depositors'
  point share. **Likely intended** (boost is a paid amplifier) → probably Medium/by-design; flag for spec check.

## Privileged (trusted-admin prerequisite → demote per L3)
- **SOPH-05 setEndBlock withdrawalBlocks=0** (sf-07): owner can lock user withdrawals. onlyOwner → not permissionless.
- **SOPH-06 add/set _withUpdate=false** (sf-06): admin retroactive reward dilution. onlyOwner.
- **SOPH-07 heldProceeds under-withdraw** (sf-08): benign accounting gap; not user-deposit theft. onlyOwner.

Duplicate/known-pattern risk: assessed WITHOUT the target answer key (sealed). stETH-wrap-vs-received and
MasterChef accPointsPerShare scaling are known *pattern classes*; specific applicability TBD at STAGE-2 scoring.
