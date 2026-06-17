# Reproduce — C-1

```bash
cd reports/cartha-2026-06-13/harness
forge test --match-contract PoC_StaleTvlMint -vv
```
PoC: `poc/PoC_StaleTvlMint.t.sol` (also in `harness/test/`). Captured output: `poc_output.log`.
Vulnerable source: `vulnerable/CarthaVault.sol` (`_convertToShares`, `_totalValueLocked`), `vulnerable/PoolDeployLib.sol` (`gmValueInUsdc`).

Expected: test passes; logs `attacker deposited 100000 / attacker claim 125000 / victim before 150000 / victim after 125000`
— a depositor mints at the stale 1e12 first-deposit rate during a TVL==0 read (GM oracle ≤0) and captures 25k of the victim's PnL.

Toolchain: `harness/SETUP.md`. Local Foundry EVM only; nothing submitted (human review + KYC + submission are the operator's responsibility).
