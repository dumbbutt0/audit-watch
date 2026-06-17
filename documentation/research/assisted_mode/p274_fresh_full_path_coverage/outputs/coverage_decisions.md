# Award-class coverage router — ADVISORY decisions

**ADVISORY ONLY. No severity / reportability / submission / routing.**

selected_classes: ACCOUNTING_LIQUIDATION_BAD_DEBT, ORDER_VALIDATION, DOS_LIVENESS, STATE_MACHINE_LIFECYCLE, SHARE_ROUNDING_PRECISION

| id | award_class | signal | recall-Δ | heavy | label |
|---|---|---|---|---|---|
| offers | ORDER_VALIDATION | 4 | - | - | **COVERAGE_SELECT** |
| pool_withdraw | SHARE_ROUNDING_PRECISION | 2 | - | - | **COVERAGE_DEFER_DUPLICATE_CLASS** |
| pool_redeem | SHARE_ROUNDING_PRECISION | 3 | - | - | **COVERAGE_SELECT** |
| pool_mint | SHARE_ROUNDING_PRECISION | 3 | - | - | **COVERAGE_DEFER_DUPLICATE_CLASS** |
| wq_mint | SHARE_ROUNDING_PRECISION | 2 | - | - | **COVERAGE_DEFER_DUPLICATE_CLASS** |
| wq_withdraw | DOS_LIVENESS | 3 | Y | - | **COVERAGE_SELECT** |
| mergeTranches | DOS_LIVENESS | 2 | Y | - | **COVERAGE_DEFER_DUPLICATE_CLASS** |
| _mergeTranches | DOS_LIVENESS | 2 | Y | - | **COVERAGE_DEFER_LOW_SIGNAL** |
| pool_constructor | STATE_MACHINE_LIFECYCLE | 2 | Y | - | **COVERAGE_DEFER_LOW_SIGNAL** |
| deployWithdrawalQueue | STATE_MACHINE_LIFECYCLE | 2 | Y | - | **COVERAGE_DEFER_LOW_SIGNAL** |
| queueClaimAll | DOS_LIVENESS | 3 | Y | - | **COVERAGE_DEFER_DUPLICATE_CLASS** |
| distribute | ACCOUNTING_LIQUIDATION_BAD_DEBT | 3 | Y | - | **COVERAGE_SELECT** |
| burnAndWithdraw | STATE_MACHINE_LIFECYCLE | 3 | Y | - | **COVERAGE_SELECT** |
| pool__withdraw | STATE_MACHINE_LIFECYCLE | 1 | Y | - | **COVERAGE_DEFER_LOW_SIGNAL** |
| settleWithBuyout | STATE_MACHINE_LIFECYCLE | 3 | Y | - | **COVERAGE_DEFER_DUPLICATE_CLASS** |
