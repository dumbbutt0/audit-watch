# Reproduce — N-1

From the persisted harness (out of /tmp):

```bash
cd reports/tiprun-2026-06-13/harness
forge test --match-contract PoC_PermissionEscalation -vv
```

PoC file: `poc/PoC_PermissionEscalation.t.sol` (also in `harness/test/`). Captured output: `poc_output.log`.

Expected: test passes; an attacker with zero starting privileges self-mints `ALLOW_ADMIN` at registration, uses
`ADMIN_SET_SIGNER_PERMISSIONS` (naming their own account as `adminAccountId`) to grant `ALLOW_WITHDRAW` on a victim,
and drains the victim's collateral (5000).

Toolchain / lib setup: see `harness/SETUP.md`. No mainnet/testnet interaction — all assertions run on a local
Foundry EVM. Nothing is submitted by this package; human review + KYC + submission are the operator's responsibility.
