# Reproduce — N-4

From the persisted harness (out of /tmp):

```bash
cd reports/tiprun-2026-06-13/harness
forge test --match-contract PoC_SettlementUnconstrained -vv
```

PoC file: `poc/PoC_SettlementUnconstrained.t.sol` (also in `harness/test/`). Captured output: `poc_output.log`.

Expected: both tests pass.
- L2 (`test_PoC_settlementMintsUnbackedCollateralAtOperatorPrice`): the operator settles a synthetic-100 position at
  an arbitrary price of 50 (no oracle/signature/conservation check) → +5000 unbacked collateral.
- L3 (`test_PoC_unbackedSettlementDrainsOtherUsersDeposits`): an account that deposited only 100 is settled at 50,
  then withdraws 5,000 real tokens out of the shared LoadingZone reserve (reserve drops 5,000; 4,900 belonged to
  other depositors) — proving real fund loss.

Trust model: the settlement trigger is operator-driven (no permissionless exploit), but the withdrawal half is
permissionless and the fund loss is proven; see `report.md` scope caveat for the Low/Medium framing.

Toolchain / lib setup: see `harness/SETUP.md`. No mainnet/testnet interaction — all assertions run on a local
Foundry EVM. Nothing is submitted by this package; human review + KYC + submission are the operator's responsibility.
