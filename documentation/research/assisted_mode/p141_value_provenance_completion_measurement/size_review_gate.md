# Audit Review Gate — size-credit-2024-06
Generated: 2026-06-04T19:11:28.284745+00:00
Target: Size Credit (C4 eval)

---

## Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Info | 0 |

---

## Validated Findings

| ID | Title | Severity | Entry Point | ICE_C | ICE_E |
|---|---|---|---|---|---|

---

## Finding Details


### Value Provenance Deep-Pass Results — advisory only

> **Advisory only — prompt-derived review evidence, NOT proof, NOT confirmed, NOT submission-ready.** Every row is `advisory_only=true`, `submission_ready=false`, `requires_human_review=true`. **Requires human review and PoC before use in any report.** Excluded from Validated Findings and the confirmed count.

| Status | Location | Decision | Confidence | Next step | Mechanism | Job |
|---|---|---|---|---|---|---|
| completed | `SellCreditMarket.validateSellCreditMarket` | needs_human | medium | human_review | Wrong-basis validation: a cash-denominated params.amount is  | VP-SellCreditMarket.validateSellCreditMarket.md |
| completed | `AccountingLibrary.debtTokenAmountToCollateralTokenAmount` | strong_clear (cleared advisory context) | high | keep_advisory | Debt->collateral unit conversion uses the correct price and  | VP-AccountingLibrary.debtTokenAmountToCollateralTokenAmount.md |
