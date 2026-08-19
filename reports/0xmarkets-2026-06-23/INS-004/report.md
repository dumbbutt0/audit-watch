# INS-004 — LP can capture insurance-fund injections by providing liquidity into a drawn-down pool before the next injection (cross-epoch economic capture)

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Business Logic Errors
- **Confidence:** Low
- **ICE:** Impact=Low · Confidence=Speculative · Exploitability=Conditional
- **Location(s):** `contracts/insurance/InsuranceFundUtils.sol:241-255 (applyDeltaToPoolAmount injection) consumed by GM share pricing`
- **Vulnerable files (bundled in `sources/`):** `LiquidationHandler.sol`, `AdlHandler.sol`, `OrderHandler.sol`, `InsuranceFundUtils.sol`

## Description

Because attemptInjectPool credits the pool via applyDeltaToPoolAmount with real pnlToken from the InsuranceVault, the MarketToken (GM) share price rises by the injected amount, and that value accrues pro-rata to whoever holds GM at injection time. An actor who deposits GM liquidity into a pool that is in drawdown (GM priced low to reflect the drawdown) and is still holding when a subsequent decrease/liquidation/ADL fires the injection captures a share of the fund-sourced restoration without having borne the original loss. The atomic single-transaction version is blocked: GM deposits/withdrawals are two-step keeper-executed and all execution paths are globalNonReentrant (LiquidationHandler.sol:47-48, AdlHandler.sol:56-57/91-92, OrderHandler.sol:246-247), so an attacker cannot deposit-then-withdraw around the injection in one tx. The residual is a cross-block timing play (deposit while drawn down, wait for the keeper to fire an injection, then withdraw), whose profitability depends on price reverting independently. Reported at Low/Low confidence as a hypothesis amplifier of INS-001 rather than a standalone exploit.

## Impact

Opportunistic LPs may extract insurance-fund value that was intended to protect the pool generally, at the expense of long-term LPs and the fund. Not a confirmed atomic exploit; an economic fairness/MEV concern conditioned on multi-block timing.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Capture trader-funded insurance reserves as an LP by being positioned in the pool when a price-driven injection (see INS-001) restores USD value.
- **Technique:** Deposit GM liquidity into a market that is in drawdown (cheap GM), remain an LP across a keeper-executed close that triggers attemptInjectPool, then redeem GM after the injection raised pool value. Requires the two-step GM deposit and the injection to fall in the actor's favorable window.
- **Evasion:** The two-step keeper deposit/withdraw flow plus globalNonReentrant deliberately prevent atomic flash-style capture; the gap is that injections are still a predictable, fund-sourced value transfer to current LPs, with no holding-period or pro-rata-loss check tying the recipient to the original loss.

## Reachability / follow-up

Conditional
