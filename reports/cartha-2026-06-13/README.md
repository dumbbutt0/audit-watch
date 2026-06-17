# Cartha Vaults audit — reproduce

Target: `cartha-vaults-main` (commit `4c51f2a…`), Foundry, `solc ^0.8.20`. Bittensor SN35 vaults over 0xMarkets GM pools.

> **Packaged deliverables:** per-finding submission packages (C-1, L-1, L-2) in `submissions/<ID>/` — each includes a
> copy of its vulnerable `src/` file(s) under `vulnerable/` (see `submissions/INDEX.md`); runnable harness in
> `harness/`; all three mirrored to the dashboard `/candidates` view via `sync_cartha_to_dashboard.py`. Full analysis:
> `FINDINGS.md`.

## Setup
```bash
# extract the zip, cd in; populate empty lib/ (forge install, or copy cached deps):
#   lib/forge-std, lib/openzeppelin-contracts (5.x), lib/openzeppelin-contracts-upgradeable (5.x), lib/solady
forge build
forge test --no-match-path 'test/fork/**'     # baseline: 283 passed / 0 failed
```
Notes: pinned OZ is v5.5 (`foundry.lock`); cached v5.4 builds with no API drift. The repo ships full 0xM mocks
(`test/mocks/Mock0xMReader|Mock0xMOracle|MockExchangeRouter|MockERC20`) so PoCs need no fork.

## Run the PoC (C-1: stale/zero-TVL share mispricing → PnL theft)
```bash
forge test --match-contract PoC_StaleTvlMint -vv
```
Expected: `test_PoC_staleTvlZeroRead_stealsPnL` **passes**, logging
`attacker deposited 100000 / attacker claim 125000 / victim before 150000 / victim after 125000`. It proves that
when the GM oracle reads `<= 0` (so `_totalValueLocked()` reads 0 while profitable GM value exists), a permissionless
`depositAndLock` mints at the stale 1e12 first-deposit rate and captures 25k of the victim's PnL.

`PoC_StaleTvlMint.t.sol` is the standalone PoC (drop into `test/`). See `FINDINGS.md` for the full analysis, the
Low/Info findings, the reviewed-and-sound surfaces, and the suggested fixes.
