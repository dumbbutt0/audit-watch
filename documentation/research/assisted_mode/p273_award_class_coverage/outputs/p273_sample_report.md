# Award-class coverage router — ADVISORY decisions

**ADVISORY ONLY. No severity / reportability / submission / routing.**

selected_classes: ORDER_VALIDATION, ACCOUNTING_LIQUIDATION_BAD_DEBT, FRONT_RUNNING_MEV

| id | award_class | signal | recall-Δ | heavy | label |
|---|---|---|---|---|---|
| init_liq_incentive | ACCOUNTING_LIQUIDATION_BAD_DEBT | 2 | Y | - | **COVERAGE_DEFER_DUPLICATE_CLASS** |
| init_health_zero | ACCOUNTING_LIQUIDATION_BAD_DEBT | 3 | Y | Y | **COVERAGE_SELECT_HEAVY** |
| init_coll_credit | ACCOUNTING_LIQUIDATION_BAD_DEBT | 3 | Y | Y | **COVERAGE_SELECT_HEAVY** |
| init_fillorder | ORDER_VALIDATION | 4 | Y | - | **COVERAGE_SELECT** |
| init_callback | FRONT_RUNNING_MEV | 2 | Y | - | **COVERAGE_SELECT** |
