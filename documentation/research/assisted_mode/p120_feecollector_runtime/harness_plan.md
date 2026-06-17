# P120 — Harness plan & feasibility

**Classification: HARNESS_MODERATE, no fork.** Like P117 (phi missing `@prb`), the ramses repo has no `node_modules`
and does not remap `@openzeppelin`, so `FeeCollector`'s `Initializable`/`SafeERC20` imports do not resolve in-repo →
a **standalone Foundry project** is used. ramses `contracts/` is imported via remapping (UNMUTATED).

## Project — `/tmp/p120-feecollector-harness/`
`foundry.toml`: solc **0.8.26** (FeeCollector uses `require(cond, CustomError())`, a 0.8.26 feature), `evm = cancun`,
`via_ir = true`, `optimizer_runs = 800`. Remappings:
```
forge-std/=lib/forge-std/src/                          (symlink -> /tmp/p89-phi/lib/forge-std)
@openzeppelin/=/tmp/p102-iqai/node_modules/@openzeppelin/   (full non-upgradeable OZ; provides Initializable, SafeERC20, ERC1967Proxy)
permit2/=/tmp/p93-ramses/lib/permit2/src/
ramses/=/tmp/p93-ramses/contracts/                     (FeeCollector.sol + all interfaces, unmutated)
```
No network needed — all deps are on-disk from prior clones.

## Deploy plan (real contract under test)
`FeeCollector`'s constructor `_disableInitializers()`, so the implementation cannot be initialized directly
(`InvalidInitialization()`). Deploy behind OZ `ERC1967Proxy`:
```solidity
FeeCollector impl = new FeeCollector();
ERC1967Proxy proxy = new ERC1967Proxy(address(impl), abi.encodeCall(FeeCollector.initialize, (treasury, voter)));
FeeCollector fc = FeeCollector(address(proxy));
```

## Mocks (only what FeeCollector calls — selector dispatch; not full interface impls)
| Mock | Implements | Behavior |
|---|---|---|
| `MockERC20` | mint/transfer/approve/transferFrom | minimal ERC20 |
| `MockPool` | `token0()`, `token1()`, `collectProtocol(address,uint128,uint128)` | sends its token balance to `recipient`, records `lastCollectRecipient` |
| `MockVoter` | `gaugeForPool`, `isAlive`, `poolRedirect`, `feeDistributorForGauge` | configurable per pool/gauge |
| `MockFeeDist` | `notifyRewardAmount(address,uint256)` | records total + pulls approved tokens via `transferFrom` (real ve(3,3)) |

`MockPool` is passed as `IRamsesV3Pool(address(mockPool))` — the cast needs only the type (imported), not a full impl.

## Actors
`treasury`, `attacker` (arbitrary EOA), `gauge` — all `makeAddr`. The attacker is the permissionless caller in every
case (no privileged setup).

## Test matrix (Cases A–D) → `FeeCollectorRuntime.t.sol`
- **A** live gauge + arbitrary caller → 20% treasury / 80% feeDist; **attacker balance == 0** before & after; FeeCollector drained.
- **B** no gauge → all fees to `treasury`; `collectProtocol` recipient == treasury; attacker 0.
- **C** attacker-deployed fake pool → voter returns gauge 0 → treasury branch; recipient hardcoded `treasury`, not attacker.
- **D** pre-seed FeeCollector residual + collect a different pool → residual swept into that pool's feeDist (balanceOf quirk); attacker gains nothing (donation/self-loss, not theft).

## Deps present?
forge-std ✓ (phi copy), OZ ✓ (iqai copy, incl. ERC1967Proxy), permit2 ✓ (ramses lib), ramses contracts ✓. solc
0.8.26 resolved by forge. → MODERATE confirmed; harness built and runs (see `runtime_matrix.md` / `execution_output.txt`).
