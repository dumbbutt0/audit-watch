# Harness prep — ramses-2024-10 :: RamsesV3Pool.swap

**Harness classification (advisory EFFORT estimate): HARNESS_COMPLEX**
_fork / external-state recreation required (external protocol integration import(s): ./interfaces/callback/IUniswapV3FlashCallback.sol, ./interfaces/callback/IUniswapV3MintCallback.sol, ./interfaces/callback/IUniswapV3SwapCallback.sol)_

> Harness preparation prepares execution; it does NOT prove exploitation and does NOT advance candidate status. The classification is an advisory EFFORT estimate, not a gate. BLOCKED means runtime infrastructure is unavailable — it is NOT a verdict that the candidate is safe or unsafe.

## Runtime prerequisites (checklist)
- [ ] **Fork** required: external protocol integration import(s): ./interfaces/callback/IUniswapV3FlashCallback.sol, ./interfaces/callback/IUniswapV3MintCallback.sol, ./interfaces/callback/IUniswapV3SwapCallback.sol
- [ ] Deploy `FixedPoint128`
- [ ] Deploy `FullMath`
- [ ] Deploy `Oracle`
- [ ] Deploy `PoolStorage`
- [ ] Deploy `Position`
- [ ] Deploy `ProtocolActions`
- [ ] Deploy `RamsesV3Factory`
- [ ] Deploy `RamsesV3Pool`
- [ ] Deploy `RamsesV3PoolDeployer`
- [ ] Deploy `SafeCast`
- [ ] Deploy `SqrtPriceMath`
- [ ] Deploy `SwapMath`
- [ ] Deploy `Tick`
- [ ] Deploy `TickBitmap`
- [ ] Deploy `TickMath`
- [ ] Deploy `TransferHelper`
- [ ] Initialize / configure to a valid pre-state
- [ ] Fund the actors that need token balances

## Actors to set up
- `attacker` — EOA entrypoint (default adversary)
- `admin` — owner/role/privileged guard present
- `victim_user` — per-user accounting present
- `liquidity_provider` — liquidity/reserve mechanics present
- `protocol` — external protocol surface (factory/pair/pool/oracle)

## Dependencies
- in-scope deployables: ['FixedPoint128', 'FullMath', 'Oracle', 'PoolStorage', 'Position', 'ProtocolActions', 'RamsesV3Factory', 'RamsesV3Pool', 'RamsesV3PoolDeployer', 'SafeCast', 'SqrtPriceMath', 'SwapMath', 'Tick', 'TickBitmap', 'TickMath', 'TransferHelper']
- external integrations (fork): ['./interfaces/callback/IUniswapV3FlashCallback.sol', './interfaces/callback/IUniswapV3MintCallback.sol', './interfaces/callback/IUniswapV3SwapCallback.sol']
- tokens: ['./interfaces/IERC20Minimal.sol', '@openzeppelin/contracts/interfaces/IERC20.sol']

## Next step
Fill the TODOs in the generated scaffold (`*.scaffold.t.sol`) to build the Stage-C runtime fixture, then let Stage C classify REPRODUCED / PARTIAL_REPRO / NOT_REPRODUCED. The scaffold is inert until you do.

