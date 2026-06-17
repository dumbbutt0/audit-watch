# TipRun audit — reproduce

Target: `tiprun-contracts-main` (commit `d5d4d2a…`), Foundry, `solc ^0.8.13`, OZ-upgradeable. Perp profile.

> **Packaged deliverables:** per-finding submission packages live in `submissions/<ID>/` (see `submissions/INDEX.md`);
> the runnable harness (out of /tmp) is `harness/` (`harness/SETUP.md`); all 6 findings are mirrored to the dashboard
> `/candidates` view via `sync_tiprun_to_dashboard.py`. Full analysis: `FINDINGS.md`.

## Setup
```bash
# extract the zip, cd in
cd tiprun-contracts-main
# populate empty submodules (forge install, or copy cached deps):
#   lib/forge-std, lib/openzeppelin-contracts (v5.x), lib/openzeppelin-contracts-upgradeable (v5.x), lib/solidity-bytes-utils
forge build            # src/ compiles; script/ uses removed OZ 4.x ProxyAdmin API (out of scope)
```

Notes on the harness (so the suite compiles under OZ 5.x):
- `script/` moved aside (deploy tooling, not in audit scope; uses OZ 4.x `ProxyAdmin()`/`getProxyImplementation`).
- `test/SetSyntheticAssetInfo.t.sol` and `test/TransactionProcessor.basic.t.sol`: `new ProxyAdmin()` →
  `new ProxyAdmin(msg.sender)` (OZ 5.x constructor takes an owner).
- `test/DeployMinimal.e2e.t.sol`, `test/DeploySpot.e2e.t.sol` moved aside (import the deploy script).
- Baseline: `387 passed / 5 failed`; the 5 failures are `vm.expectRevert` legacy-string mismatches vs OZ 5.4
  custom errors — test-only, not contract bugs.

## Run the PoC (F-1: maintenance-margin bypass on collateral withdrawal)
```bash
forge test --match-contract PoC_MarginBypassWithdraw -vv
```
Expected: `test_PoC_withdrawAllCollateralWhileHoldingPosition` **passes**, logging
`value before = 15000·FXP`, `value after = 5000·FXP`, `tokens extracted: 10000`. It proves a user withdrew 100% of
collateral (10 000 tokens left `LoadingZone`) while keeping a long position, leaving the account under maintenance
margin (`risk > value·FXP`) — a transition the margin check should have reverted.

## Run the PoC (M-1: de-risk DoS — inverted ratio guard)
```bash
forge test --match-contract PoC_DeriskDoS -vv
```
Expected: `test_PoC_cannotPartiallyDeriskUnhealthyAccount` **passes**. From an under-margin account, a fair *partial*
de-risk (sell 500 synthetic for 500 collateral) reverts with `PM: val/risk dec`, while a larger de-risk that reaches
full health succeeds — demonstrating that `Risk.checkValidTransition` blocks incremental recovery of unhealthy
accounts.

## Run the PoC (F-2: account freeze / liquidation lock past the top risk segment)
```bash
forge test --match-contract PoC_RiskSegmentFreeze -vv
```
Expected: `test_PoC_priceRiseFreezesAccountAndBlocksLiquidation` **passes**. A long 5,000 at price 1 (notional
5,000 ≤ cap 10,000) is healthy; after the oracle price rises to 3 (notional 15,000 > 10,000), the risk engine, any
position resize (liquidation/de-risk) and a withdrawal all revert with `Risk: no risk` — the account is frozen and
cannot be liquidated.

See `FINDINGS.md` for root-cause analysis and suggested fixes. Four standalone PoCs (drop into `test/`):
`PoC_MarginBypassWithdraw.t.sol` (F-1), `PoC_RiskSegmentFreeze.t.sol` (F-2), `PoC_DeriskDoS.t.sol` (M-1).
