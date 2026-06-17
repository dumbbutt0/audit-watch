# Reproduce — M-2

From the persisted harness (out of /tmp):

```bash
cd reports/tiprun-2026-06-13/harness
forge test --match-contract PoC_OracleStaleness -vv
```

PoC file: `poc/PoC_OracleStaleness.t.sol` (also in `harness/test/`). Captured output: `poc_output.log`.

Expected: test passes; an older-timestamp price is accepted (no monotonic guard) and a 10-year-old price still reads exist=true (no staleness).

Toolchain / lib setup: see `harness/SETUP.md`. No mainnet/testnet interaction — all assertions run on a local
Foundry EVM. Nothing is submitted by this package; human review + KYC + submission are the operator's responsibility.
