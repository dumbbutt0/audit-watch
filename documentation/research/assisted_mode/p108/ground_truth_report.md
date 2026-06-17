# P108 — Ground-truth report

The self-kill layer must spare real findings. It FAILS if it kills P104 or a majority of awarded findings.

## Confirmed PoC (P104)
- IQ-AI M-01 state: **SURVIVED** (required: SURVIVED)
- HS_p104_killed tripped: False

## Awarded findings (known-good real bugs)
- total awarded: 15
- awarded KILLED: 0 
- awarded survived/held (not killed): 15
- HS_majority_awarded_killed tripped: False

## Per-awarded state
| Subject | finding fn | state |
|---|---|---|
| iq-ai-2025-01 | moveLiquidity | SURVIVED |
| kleidi-2024-10 | checkCalldata | SURVIVED |
| munchables-2024-07 | transferToUnoccupiedPlot | SURVIVED |
| phi-2024-08 | _removeCredIdPerAddress | SURVIVED |
| phi-2024-08 | buyShareCredFor | SURVIVED |
| ramses-2024-10 | flash | SURVIVED |
| ramses-2024-10 | getPeriodReward | SURVIVED |
| secondswap-2024-12 | claimable | SURVIVED |
| secondswap-2024-12 | transferVesting | SURVIVED |
| secondswap-2024-12 | spotPurchase | SURVIVED |
| traitforge-2024-07 | forgeWithListed | SURVIVED |
| traitforge-2024-07 | mintWithBudget | SURVIVED |
| vultisig-2024-06 | claim | SURVIVED |
| wildcat-2024-08 | grantRole | SURVIVED |
| wildcat-2024-08 | executeWithdrawal | SURVIVED |

## Conclusion
- The layer PRESERVES the awarded findings and KEEPS P104.
- Honest residual: awarded findings landing in NEEDS_RUNTIME are the cross-contract / runtime-bound class (source-only self-kill correctly declines to judge them).

