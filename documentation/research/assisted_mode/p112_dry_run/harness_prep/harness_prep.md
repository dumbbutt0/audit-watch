# Harness prep — iq-ai-2025-01 :: LiquidityManager.moveLiquidity

**Harness classification (advisory EFFORT estimate): HARNESS_COMPLEX**
_fork / external-state recreation required (2 hardcoded mainnet address(es); external protocol integration import(s): dev-fraxswap/src/contracts/core/interfaces/IFraxswapFactory.sol, dev-fraxswap/src/contracts/core/interfaces/IFraxswapPair.sol, dev-fraxswap/src/contracts/core/libraries/Math.sol)_

> Harness preparation prepares execution; it does NOT prove exploitation and does NOT advance candidate status. The classification is an advisory EFFORT estimate, not a gate. BLOCKED means runtime infrastructure is unavailable — it is NOT a verdict that the candidate is safe or unsafe.

## Runtime prerequisites (checklist)
- [ ] **Fork** required: 2 hardcoded mainnet address(es); external protocol integration import(s): dev-fraxswap/src/contracts/core/interfaces/IFraxswapFactory.sol, dev-fraxswap/src/contracts/core/interfaces/IFraxswapPair.sol, dev-fraxswap/src/contracts/core/libraries/Math.sol
- [ ] Deploy `AgentFactory`
- [ ] Deploy `BootstrapPool`
- [ ] Deploy `LiquidityManager`
- [ ] Fund the actors that need token balances

## Actors to set up
- `attacker` — EOA entrypoint (default adversary)
- `victim_user` — per-user accounting present
- `liquidity_provider` — liquidity/reserve mechanics present
- `protocol` — external protocol surface (factory/pair/pool/oracle)

## Dependencies
- in-scope deployables: ['AgentFactory', 'BootstrapPool', 'LiquidityManager']
- external integrations (fork): ['dev-fraxswap/src/contracts/core/interfaces/IFraxswapFactory.sol', 'dev-fraxswap/src/contracts/core/interfaces/IFraxswapPair.sol', 'dev-fraxswap/src/contracts/core/libraries/Math.sol']
- tokens: ['@openzeppelin/contracts/interfaces/IERC20.sol', '@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol']

## Next step
Fill the TODOs in the generated scaffold (`*.scaffold.t.sol`) to build the Stage-C runtime fixture, then let Stage C classify REPRODUCED / PARTIAL_REPRO / NOT_REPRODUCED. The scaffold is inert until you do.

