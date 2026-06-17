# Reproduce — M-1

From the persisted harness (out of /tmp):

```bash
cd reports/tiprun-2026-06-13/harness
forge test --match-contract PoC_DeriskDoS -vv
```

PoC file: `poc/PoC_DeriskDoS.t.sol` (also in `harness/test/`). Captured output: `poc_output.log`.

Expected: test passes; a fair partial de-risk of an under-margin account reverts 'PM: val/risk dec', while a full de-risk to health succeeds.

Toolchain / lib setup: see `harness/SETUP.md`. No mainnet/testnet interaction — all assertions run on a local
Foundry EVM. Nothing is submitted by this package; human review + KYC + submission are the operator's responsibility.
