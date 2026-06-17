# P207 — dependency assembly (the exact blocker that kept P205 partial)

## Resolved — both deps installed by tag into the isolated project (`pocs/p207/lib/`)
| dependency | source | tag / commit | solidity | why compatible |
|---|---|---|---|---|
| OpenZeppelin Contracts **3.4.x** | `github.com/OpenZeppelin/openzeppelin-contracts` | `v3.4.0` (`7985e4d0`) | `>=0.6.0 <0.8.0` | OZ 3.x line targets 0.6/0.7; `ERC721.sol` carries built-in enumerable (`tokenOfOwnerByIndex`) needed by ILOPool |
| Uniswap **v3-core** | `github.com/Uniswap/v3-core` | `v1.0.0` (`ef64f51d`) | `>=0.4.0` … `=0.7.6` | the canonical 0.7.6-era v3-core; supplies `IUniswapV3Pool/Factory`, `callback/IUniswapV3MintCallback`, math libs `FullMath`/`TickMath`/`SqrtPriceMath`/`FixedPoint128`/`FixedPoint96`/`UnsafeMath` |

## Why NO v3-periphery is needed (P205's feared blocker is moot)
Vultisig vendors its own periphery pieces locally in `src/`: `base/PeripheryPayments.sol`, and
`libraries/{PoolAddress,LiquidityAmounts,TransferHelper,SqrtPriceMathPartial,PositionKey,ChainId}.sol`. So the only
external imports are OZ 3.4 + v3-core (above). This is far lighter than P205's worst-case assumption.

## Remappings (`pocs/p207/foundry.toml`, solc 0.7.6)
```
@openzeppelin/=lib/openzeppelin-contracts-3.4/
@uniswap/v3-core/=lib/v3-core/
vult/=realsrc/src/
```
(Initial attempt used `@openzeppelin/=…/contracts/` which doubled `contracts/contracts/`; corrected to the repo root.)

## Mocks / adapters (external-only, not the analysis locus)
- `MockERC20` — faithful ERC20 (mint/approve/transfer) for raise/sale tokens.
- `ManagerStub` — supplies the source-valid `IILOManager.Project` and acts as `MANAGER` (caller of
  `initialize`/`launch`). Adds NO vulnerable logic; the REAL `ILOPool`/`ILOManager` bytecode runs unmodified.
- `FaithfulV3Pool` — canonical single-position V3 pool (mint/burn-poke/positions/collect + fee growth) for the H-01
  harness; not rigged (see `H01_POSITIVE_CONTROL_POC.md`).
- ILOPool is deployed via `Clones.clone(impl)` because its constructor calls `_disableInitialize()` (clone pattern),
  matching the real factory.

No original Vultisig source edited; `realsrc/src` byte-identical to production (`d9489e47`).
