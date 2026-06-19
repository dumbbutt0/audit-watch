# Reproduce — N-4

From the persisted harness (out of /tmp):

```bash
cd reports/tiprun-2026-06-13/harness
forge test --match-contract PoC_SettlementUnconstrained -vv
```

PoC file: `poc/PoC_SettlementUnconstrained.t.sol` (also in `harness/test/`). Captured output: `poc_output.log`.

Expected: test passes. An account holds synthetic 100 with oracle price 1; the operator settles at an arbitrary price
of 50 (no oracle/signature/conservation check). The synthetic is zeroed and collateral is credited by exactly
`balance * operatorPrice = 5000` — unbacked, later-withdrawable collateral.

Trust model: settlement is operator-driven, so there is no permissionless exploit; this is a missing on-chain
invariant (see `report.md` scope caveat).

Toolchain / lib setup: see `harness/SETUP.md`. No mainnet/testnet interaction — all assertions run on a local
Foundry EVM. Nothing is submitted by this package; human review + KYC + submission are the operator's responsibility.
