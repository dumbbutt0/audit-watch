# Reproduce — F-2

From the persisted harness (out of /tmp):

```bash
cd reports/tiprun-2026-06-13/harness
forge test --match-contract PoC_RiskSegmentFreeze -vv
```

PoC file: `poc/PoC_RiskSegmentFreeze.t.sol` (also in `harness/test/`). Captured output: `poc_output.log`.

Expected: both tests pass; once notional exceeds the top risk segment, getAccountPositionStatus / any resize / liquidation / withdrawal all revert 'Risk: no risk' — incl. an insolvent short that cannot be liquidated.

Toolchain / lib setup: see `harness/SETUP.md`. No mainnet/testnet interaction — all assertions run on a local
Foundry EVM. Nothing is submitted by this package; human review + KYC + submission are the operator's responsibility.
