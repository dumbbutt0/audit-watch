# P110 — Harness feasibility report

**Invariant:** Scaffold generation prepares execution; it never proves exploitation and never upgrades candidate status.  ·  research-only, un-wired.

_Answers 'what would it take to execute this candidate?' — never 'does it exploit?'. No candidate status is advanced; this layer produces no rating, no finding state, and no downstream-readiness state._

## Metrics
- total candidates: 28 — SIMPLE=1 MODERATE=14 COMPLEX=13 BLOCKED=0
- average dependencies: 7.393 · average actors: 3.321 · average setup steps: 7.429

## Positive controls

| control | classification | fork | rationale |
|---|---|---|---|
| iq-ai-2025-01:moveLiquidity | HARNESS_COMPLEX | True | fork / external-state recreation required (2 hardcoded mainnet address(es); external protocol integration import(s): dev-fraxswap/src/contracts/core/interfaces/IFraxswapFactory.sol, dev-fraxswap/src/contracts/core/interfaces/IFraxswapPair.sol, dev-fraxswap/src/contracts/core/libraries/Math.sol) |
| secondswap-2024-12:spotPurchase | HARNESS_MODERATE | False | 6 in-scope contract(s), local deploy with ordering / initialization |

## Per-candidate

| Subject | Contract.fn | class | fork | deps | actors | setup | blockers |
|---|---|---|---|---|---|---|---|
| vultisig-2024-06 | ILOManager.initialize | HARNESS_COMPLEX | True | 4 | 5 | 7 | - |
| vultisig-2024-06 | Multicall.multicall | HARNESS_SIMPLE | False | 1 | 1 | 1 | - |
| phi-2024-08 | PhiNFT1155.claimFromFactory | HARNESS_MODERATE | False | 5 | 3 | 7 | - |
| phi-2024-08 | PhiFactory.claim | HARNESS_MODERATE | False | 2 | 4 | 4 | - |
| phi-2024-08 | Claimable.signatureClaim | HARNESS_MODERATE | False | 2 | 2 | 2 | - |
| phi-2024-08 | PhiNFT1155.createArtFromFactory | HARNESS_MODERATE | False | 5 | 3 | 7 | - |
| phi-2024-08 | Claimable.merkleClaim | HARNESS_MODERATE | False | 2 | 2 | 2 | - |
| phi-2024-08 | PhiFactory.updateArtSettings | HARNESS_MODERATE | False | 2 | 4 | 4 | - |
| phi-2024-08 | PhiNFT1155.initialize | HARNESS_MODERATE | False | 5 | 3 | 7 | - |
| kleidi-2024-10 | RecoverySpell.executeRecovery | HARNESS_COMPLEX | True | 1 | 3 | 2 | - |
| kleidi-2024-10 | AddressCalculation.calculateAddressUnsafe | HARNESS_MODERATE | False | 5 | 3 | 5 | - |
| kleidi-2024-10 | SystemDeploy.deploy | HARNESS_COMPLEX | True | 7 | 3 | 8 | - |
| kleidi-2024-10 | SystemDeploy.validate | HARNESS_COMPLEX | True | 7 | 3 | 8 | - |
| ramses-2024-10 | RamsesV3Pool.swap | HARNESS_COMPLEX | True | 16 | 5 | 19 | - |
| ramses-2024-10 | GaugeV3.cachePeriodEarned | HARNESS_COMPLEX | False | 7 | 5 | 8 | - |
| ramses-2024-10 | RamsesV3Pool.initialize | HARNESS_COMPLEX | True | 16 | 5 | 19 | - |
| ramses-2024-10 | Position.positionPeriodSecondsInRange | HARNESS_COMPLEX | False | 10 | 3 | 11 | - |
| ramses-2024-10 | RamsesV3Pool._advancePeriod | HARNESS_COMPLEX | True | 16 | 5 | 19 | - |
| ramses-2024-10 | Position._updatePosition | HARNESS_COMPLEX | False | 10 | 3 | 11 | - |
| wildcat-2024-08 | WildcatMarket.closeMarket | HARNESS_MODERATE | False | 6 | 3 | 7 | - |
| wildcat-2024-08 | WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches | HARNESS_MODERATE | False | 4 | 3 | 5 | - |
| wildcat-2024-08 | WildcatMarket.borrow | HARNESS_MODERATE | False | 6 | 3 | 7 | - |
| wildcat-2024-08 | WildcatMarket.repay | HARNESS_MODERATE | False | 6 | 3 | 7 | - |
| secondswap-2024-12 | SecondSwap_Marketplace.doesFunctionExist | HARNESS_MODERATE | False | 6 | 3 | 8 | - |
| iq-ai-2025-01 | AgentRouter.buy | HARNESS_COMPLEX | True | 4 | 3 | 6 | - |
| iq-ai-2025-01 | AgentRouter.sell | HARNESS_COMPLEX | True | 4 | 3 | 6 | - |
| iq-ai-2025-01 | AgentRouter.getAmountOut | HARNESS_COMPLEX | True | 4 | 3 | 6 | - |
| iq-ai-2025-01 | Agent.setProxyImplementation | HARNESS_MODERATE | False | 3 | 4 | 5 | - |

## Reading
- Classification estimates the human effort to build a runtime harness; it does not estimate whether the candidate is exploitable.
- A ready setUp skeleton + dependency/actor/environment checklist per candidate is the effort-reduction deliverable (see scaffolds/).

