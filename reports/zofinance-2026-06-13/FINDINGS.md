# ZO Finance (Sui Move perpetuals) — audit findings

Date: 2026-06-13 · Real hunt, local-only, **nothing submitted**, no finding manufactured.
Repo: `zofinance/zo-contracts-public` @ `ec48af4` (in-scope `zo-core`; `vendor/` = pyth/wormhole/sudo_nft deps).
HackenProof Sui Security Expansion — **ZO Finance Smart Contracts** bug bounty (Crit $10k / High $5k). GMX-style
**pool-counterparty perpetuals** on Sui (LP pool is the trader counterparty). 5th Sui-Move target validating
Audit-Watch's Move support ([[project_move_support]]; after turbos CLMM, Ember vault, Suilend + Scallop lending).
**Caveats: the ZO bug bounty currently shows "Paused" on HackenProof; user to confirm status + rep ≤80 on dashboard.**

## STATUS: source audit of the perps CORE → no permissionless bug found (clean). Honest, scope-limited.
The build is blocked (see below) and the bounty is paused, so this is a **source-level** audit (no runnable PoC yet).
The core perps logic (signed math, position lifecycle, PnL, per-side funding, liquidation, decrease settlement) was
deep-read and is carefully built; the LP-pool valuation/accounting layer (`pool.move` deposit/withdraw/valuate +
`market.move` ~3.5k SLOC) is the **remaining, not-yet-exhausted** surface.

## Reviewed and SOUND
- **Signed math** (`math/sdecimal.move`, `srate.move`): add/sub/mul/div sign logic correct (same-sign add, larger-
  magnitude-sign on subtract, XNOR sign on mul/div), zero handled. The PnL/funding sign foundation is solid.
- **PnL** (`position.move::compute_delta_size`): `latest=index×amount` vs entry `position_size`; profit sign =
  `long` when price up, `!long` when down — correct long/short PnL.
- **Funding** (`compute_funding_fee_value` + `pool.move::refresh_symbol`/`symbol_delta_funding_rate`): per-symbol
  `acc_funding_rate` (signed), rate driven by `symbol_pnl_per_lp` (skew vs LP supply, GMX-style). Symbols are keyed
  `SymbolName<I,D>` ⇒ **separate Symbol per side (long/short)**, each with its own funding accumulator, so applying
  the rate uniformly within a side is correct (no long/short funding-sign bug).
- **decrease/close settlement** (`position.move::decrease_position`): PnL pro-rated by `decrease_amount/amount`;
  fees (reserving/funding/decrease) subtracted via signed math; **profit `floor` + capped by `position.reserved`**
  (pool can't be overpaid → position auto-closes if reserved insufficient); **loss `ceil` + capped by `collateral`**;
  fees rounded up. Rounding consistently favors the protocol; profit paid from `reserved`, loss to vault.
- **Leverage / liquidation** (`check_leverage`, `check_liquidation`): notional ≤ collateral×max_leverage; liquidatable
  when loss ≥ collateral×liquidation_threshold (and never when in profit). Standard maintenance-margin.
- **Open** (`open_position`): collateral price threshold, min collateral, leverage check; reserved allocated to back
  max profit.

## Build blocker (toolchain)
`sui move build` fails: `Move.toml` has empty `[addresses]` (`pyth=""`, `sudo_nft=""`) and empty Sui `rev`; the
vendored deps (pyth/wormhole/sudo_nft) likewise use empty named addresses assigned at publish. `Move.lock` pins the
Sui framework at **`mainnet-v1.38.3`** (older than the local `sui 1.72.5`, edition `2024.beta`). A runnable PoC
harness requires assigning all named addresses in a build copy + reconciling the old framework rev with the local
compiler — fixable but non-trivial; deferred because (a) no candidate found yet and (b) the bounty is paused.

## Not yet exhausted (remaining surface)
- `pool.move` (1565): LP deposit/withdraw, `valuate_symbol` (LP/AUM pricing), reserved allocation, and the
  **pool↔trader conservation** (can a trader extract more than reserved/their margin via the LP-pricing path).
- `market.move` (3554): the open/increase/decrease/liquidate entry orchestration, symbol management, fee routing,
  `force_settle`, and oracle (`agg_price` + Pyth) freshness on the market entry paths.
- `orders.move` (504): limit-order placement/execution/cancellation.

## Bottom line
The ZO perps **core** (signed math, position PnL/funding/liquidation, decrease settlement) is carefully built with
pool-favoring rounding, per-side funding, and profit capped by reserved — no permissionless extraction found at the
core. This is a **source-level honest-negative-so-far**; the LP-pool/market orchestration layer + a runnable PoC
(needs the build fix) remain for a complete pass. Nothing submitted; no finding manufactured. Bounty is paused.
