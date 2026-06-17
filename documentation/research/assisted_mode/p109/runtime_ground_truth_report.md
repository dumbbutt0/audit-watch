# P109 — Runtime ground-truth report

Positive control P104 must survive; awarded findings must not be runtime-killed.

- **P104 state: SURVIVED_RUNTIME** (required SURVIVED_RUNTIME) · execution-backed: True
- HS1 positive-control tripped: False
- awarded total: 2 · awarded runtime-killed: none
- HS2 historical-safety tripped: False
- HS3 execution-evidence tripped: False

## Positive controls

| id | fn | state | execution-backed |
|---|---|---|---|
| iq-ai-2025-01 | moveLiquidity | SURVIVED_RUNTIME | True |
| secondswap-2024-12 | spotPurchase | SURVIVED_RUNTIME | True |

## Conclusion
- The layer KEEPS P104 and kills no awarded findings — runtime self-kill is SAFE. Kill power is harness-gated (see main report).

