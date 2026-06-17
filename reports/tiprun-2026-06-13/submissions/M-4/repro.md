# Reproduce — M-4

From the persisted harness (out of /tmp):

```bash
cd reports/tiprun-2026-06-13/harness
forge test --match-contract PoC_ConfigVersionNotBumped -vv
```

PoC file: `poc/PoC_ConfigVersionNotBumped.t.sol` (also in `harness/test/`). Captured output: `poc_output.log`.

Expected: test passes; setSyntheticAssetsInfo leaves configVersion unchanged while setMaxFundingRate increments it.

Toolchain / lib setup: see `harness/SETUP.md`. No mainnet/testnet interaction — all assertions run on a local
Foundry EVM. Nothing is submitted by this package; human review + KYC + submission are the operator's responsibility.
