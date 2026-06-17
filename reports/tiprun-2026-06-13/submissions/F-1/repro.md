# Reproduce — F-1 + M-1 (combined report)

Both manifestations share one root cause (`Risk.checkValidTransition`); each has its own passing PoC.
From the persisted harness (out of /tmp):

```bash
cd reports/tiprun-2026-06-13/harness
forge test --match-contract PoC_MarginBypassWithdraw -vv   # Manifestation A (F-1, Critical)
forge test --match-contract PoC_DeriskDoS -vv              # Manifestation B (M-1, Medium)
```

PoC files: `poc/PoC_MarginBypassWithdraw.t.sol` and `poc/PoC_DeriskDoS.t.sol` (also in `harness/test/`).
Captured combined output: `poc_output.log`.

Expected:
- **A** — passes; account withdraws 100% collateral (10,000 tokens leave LoadingZone) while its long 5,000 position
  stays open and under maintenance margin (risk > value*FXP).
- **B** — passes; a fair partial de-risk of an under-margin account reverts `PM: val/risk dec`, while a full de-risk
  to health succeeds.

Toolchain / lib setup: see `harness/SETUP.md`. No mainnet/testnet interaction — all assertions run on a local
Foundry EVM. Nothing is submitted by this package; human review + KYC + submission are the operator's responsibility.
