# Monetrix (Code4rena 2026-04) — Awarded Findings

> Revealed AFTER blind discovery (fetched from code4rena.com/reports/2026-04-monetrix at reveal time).

# High Risk Findings (0)

# Medium Risk Findings (1)

## [[M-01] PM borrow liabilities are omitted from backing, allowing phantom surplus settlement](https://code4rena.com/reports/2026-04-monetrix)

`suppliedBalance()` only decodes the supply field from the 0x811 precompile response while discarding the
borrow liability information. This lets the system report positive surplus while the PM (portfolio-margin)
account is net underwater after borrow debt, enabling false yield distributions through the settlement gates.

# Low Risk and Non-Critical Issues

(excluded from reach denominator)
