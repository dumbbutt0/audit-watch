# Reproduce — M-3

From the persisted harness (out of /tmp):

```bash
cd reports/tiprun-2026-06-13/harness
forge test --match-contract PoC_NoLiquidatablePrecondition -vv   # liquidate
forge test --match-contract PoC_DeleverageNoConsent -vv          # deleverage
```

PoC files: `poc/PoC_NoLiquidatablePrecondition.t.sol` and `poc/PoC_DeleverageNoConsent.t.sol` (also in
`harness/test/`). Captured output: `poc_output.log`.

Expected: both pass. Liquidate force-closes a provably healthy account's position with no maintenance-margin
precondition; deleverage force-trades a provably healthy account (naming its own owner address as a registered
signer) with no signature, no nonce, and no health precondition.

Toolchain / lib setup: see `harness/SETUP.md`. No mainnet/testnet interaction — all assertions run on a local
Foundry EVM. Nothing is submitted by this package; human review + KYC + submission are the operator's responsibility.
