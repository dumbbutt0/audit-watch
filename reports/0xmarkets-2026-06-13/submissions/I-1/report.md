# I-1 (Medium, design) — Insurance injection compensates *current* LP holders, not drawdown-era holders (JIT capture)

- **Target:** 0xMarkets (GMX Synthetics fork), commit `e94daee…`.
- **Vulnerable files (copied in `vulnerable/`):** `contracts/insurance/InsuranceFundUtils.sol` (`attemptInjectPool`,
  `getDrawdownFraction`), `contracts/position/DecreasePositionCollateralUtils.sol` (call site, line ~557).
- **Severity:** Medium (value-distribution flaw; design).
- **Proof type:** code analysis (no runnable PoC — requires the full GMX deposit/withdrawal/keeper machinery).

## Root cause
When realized pool drawdown (live pool USD vs the epoch snapshot) exceeds the per-market trigger, `attemptInjectPool`
transfers insurance reserve into `MarketToken` and credits the pool via `applyDeltaToPoolAmount`, raising the
market-token price for **whoever holds LP at injection time**. The reserve was funded over the epoch by
liquidation-fee slices and is intended to compensate the LPs who *bore* the drawdown. Because compensation lands on
the pool (not a per-LP/per-epoch snapshot), an LP who deposits **after** the drawdown (and before/at injection)
captures a pro-rata share of the injected reserve they never lost.

## Impact
Mis-distribution of insurance compensation: a just-in-time LP dilutes the intended beneficiaries and skims the
insurance reserve. GMX deposits/withdrawals are async + fee'd (limiting pure single-block JIT), which bounds but does
not eliminate the mismatch.

## Fix
Gate injection eligibility by a per-share drawdown epoch (track who held LP during the loss), or restrict deposits
while a market is in a drawdown-injection state, or pay compensation to a snapshot of pre-drawdown holders rather than
to the live pool.

## Note
Not standalone-reproducible without standing up the full GMX deposit/withdrawal + keeper flow; reported as a
code-verified design finding (`InsuranceFundUtils.attemptInjectPool`).

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Blockchain → Transaction-Ordering Dependence (TOD) / Front Running (insurance injection compensates *current* LP holders, not the drawdown-era holders → JIT capture of the insurance reserve)
- **Secondary category:** Business Logic Errors (value-attribution mismatch in `attemptInjectPool`)
- **CWE (informative):** CWE-362 (Race Condition / TOD); CWE-840 (Business Logic Errors)

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| JIT insurance-reserve capture | `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N` | **3.7** | Low |

> Design finding (analysis-only, no standalone PoC — needs full GMX build). CVSS band Low; design severity Medium (value redistribution among LPs, timing-dependent).

> CVSS v3.1 base scores computed with the official formula (no temporal/environmental modifiers). For smart-contract findings the protocol/bounty severity may differ from the CVSS band; both are stated where they diverge.

<!-- END classification-cvss -->
