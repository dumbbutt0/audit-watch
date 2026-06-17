# P143 — Harness Design

**harness_type: real_contract** (the real `NoyaValueOracle` is deployed and its real public `getValue` is called).

Location: `audits/noya-2024-04-eval/pocs/p143/` (Foundry project, local to the noya eval audit — constraint 11).
- `foundry.toml` — solc 0.8.20, evm paris; remappings `@openzeppelin/contracts-5.0/` → OZ v5.0.2,
  `noya/` → the real noya contracts tree; `allow_paths` for that tree.
- `test/NoyaValueOracleMultiHopValueProvenance.t.sol` — the PoC.
- `lib/` — `forge-std` v1.9.4 + `openzeppelin-contracts` v5.0.2 (build deps; removable, see test_commands.md).

## Contracts in the test
- **`NoyaValueOracle` (REAL, imported `noya/...`)** — the subject; unmodified production source.
- **`StubRegistry`** (test mock) — `hasRole→true`, `MAINTAINER_ROLE→0x00`; passed (cast to `PositionRegistry`) so
  the **real** `onlyMaintainer` setters run. The valuation read path never reads it.
- **`TablePriceOracle`** (test mock, implements real `INoyaValueOracle`) — per-pair wad prices.
- **`CorrectedReferenceOracle`** (test control) — a copy of the real loop + resolver with **exactly one change**:
  the per-hop call uses the loop-carried `quotingToken` instead of the static `asset`. Used only to compute the
  corrected output for comparison (constraint 14).

## Why a real-contract harness was achievable
`NoyaValueOracle._getValue` depends only on its own mappings + the tiny `INoyaValueOracle` interface; `registry`
is touched only by the setters. So no heavyweight protocol deployment was needed — a stub registry + mock oracles
suffice, and the **real** `getValue`/`_getValue`/setters execute unmodified. No production contract was edited
(constraint 2): all mocks/controls live in the test file.

## Test functions (neutral names — constraint 15)
1. `test_vulnerable_multi_hop_uses_static_asset_and_misvalues` — real `getValue` returns 20e18 ≠ corrected 6e18.
2. `test_corrected_reference_uses_loop_carried_quote_token` — corrected reference returns 6e18.
3. `test_single_hop_control_matches` — one-source route: real == corrected.
4. `test_equivalent_price_control_no_divergence` — equal per-hop prices: real == corrected.
