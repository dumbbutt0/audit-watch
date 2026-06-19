# Reproduce — M-4

From the persisted harness (out of /tmp):

```bash
cd reports/tiprun-2026-06-13/harness
forge test --match-contract PoC_ConfigVersionNotBumped -vv
```

PoC file: `poc/PoC_ConfigVersionNotBumped.t.sol` (also in `harness/test/`). Captured output: `poc_output.log`.

Expected: test passes. L2 — `setSyntheticAssetsInfo` leaves `configVersion` unchanged while `setMaxFundingRate`
increments it. L3 — a user batch carrying the stale `configVersion` is accepted by `processMultiTransactions` after
`setSyntheticAssetsInfo` (guard never fires), but the identical stale batch is rejected after the version-bumping
`setMaxFundingRate`.

Toolchain / lib setup: see `harness/SETUP.md`. No mainnet/testnet interaction — all assertions run on a local
Foundry EVM. Nothing is submitted by this package; human review + KYC + submission are the operator's responsibility.
