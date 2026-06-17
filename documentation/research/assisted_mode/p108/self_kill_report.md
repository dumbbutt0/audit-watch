# P108 — Adversarial self-kill: results

**Invariant:** Self-kill exists to challenge candidates, not to approve them. A survivor is merely worthy of further investigation.  ·  research-only, un-wired.
Scope: top-10 of the P107 `recommended` ranking + awarded ground truth + the P104 confirmed candidate.

## Verdict
- **SAFETY PASS: True**  ·  **KILL-POWER PASS: False**  ·  **OVERALL PASS: False**
- SAFETY PASS / KILL-POWER FAIL — source-only self-kill is correctly conservative (0 awarded killed, P104 survives, no hard stop) but cannot eliminate any top-K candidate from source alone: top-K is selected for looking exploitable, and every source signal that would kill a weak candidate also hits an awarded one (exploitable views/role-guarded findings). The 28 NEEDS_RUNTIME candidates show the dispute is runtime-bound — elimination must come from RUNTIME execution (attempt the exploit), not more source heuristics.
- weak eliminated: False · strong survive: True · P104 survives: True · precision↑ w/o recall harm: False · no hard stop: True

## Metrics
- total candidates: **97**  ·  by state: {'KILLED': 0, 'SURVIVED': 63, 'NEEDS_RUNTIME': 28, 'NEEDS_CONTEXT': 6}
- kill_rate: 0.0 · survival_rate: 0.6495
- presumed-weak (non-awarded top-K): n=82, kill_rate=0.0, by_state={'KILLED': 0, 'SURVIVED': 48, 'NEEDS_RUNTIME': 28, 'NEEDS_CONTEXT': 6}
- known-good (awarded): n=15, survival(incl needs_*)=1.0, killed=none
- killed ranks: []

## Hard stops
- **HS_p104_killed** — tripped: False
- **HS_majority_awarded_killed** — tripped: False  {'killed': 0, 'of': 15}
- **HS_kill_by_uncertainty** — tripped: False  {'kills_without_defense_basis': []}
- **HS_runtime_mislabeled_as_killed** — tripped: False  {'cases': []}
- **HS_new_states_or_fields** — tripped: False  {'bad_states': [], 'forbidden_tokens': []}

## Candidate states (KILLED / NEEDS_RUNTIME / NEEDS_CONTEXT shown; survivors summarised)

| Subject | Contract.fn | rank | awarded | state | basis/reason |
|---|---|---|---|---|---|
| kleidi-2024-10 | IMorphoBase.withdraw | 5 |  | NEEDS_CONTEXT | insufficient source: function body not resolvable from in-sc |
| kleidi-2024-10 | WETH9.withdraw | 7 |  | NEEDS_CONTEXT | insufficient source: function body not resolvable from in-sc |
| kleidi-2024-10 | IMorphoBase.withdrawCollateral | 6 |  | NEEDS_CONTEXT | insufficient source: function body not resolvable from in-sc |
| secondswap-2024-12 | SecondSwap_Vesting.claim | 9 |  | NEEDS_CONTEXT | insufficient source: function body not resolvable from in-sc |
| secondswap-2024-12 | SecondSwap_Vesting.claimable | 10 |  | NEEDS_CONTEXT | insufficient source: function body not resolvable from in-sc |
| secondswap-2024-12 | IMarketplaceSetting.feeCollector | 7 |  | NEEDS_CONTEXT | insufficient source: function body not resolvable from in-sc |
| iq-ai-2025-01 | AgentRouter.buy | 1 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| iq-ai-2025-01 | AgentRouter.getAmountOut | 5 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| iq-ai-2025-01 | AgentRouter.sell | 2 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| iq-ai-2025-01 | Agent.setProxyImplementation | 9 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| kleidi-2024-10 | AddressCalculation.calculateAddressUnsafe | 2 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| kleidi-2024-10 | SystemDeploy.deploy | 3 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| kleidi-2024-10 | RecoverySpell.executeRecovery | 1 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| kleidi-2024-10 | SystemDeploy.validate | 4 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| phi-2024-08 | PhiFactory.claim | 3 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| phi-2024-08 | PhiNFT1155.claimFromFactory | 1 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| phi-2024-08 | PhiNFT1155.createArtFromFactory | 5 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| phi-2024-08 | PhiNFT1155.initialize | 10 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| phi-2024-08 | Claimable.merkleClaim | 6 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| phi-2024-08 | Claimable.signatureClaim | 4 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| phi-2024-08 | PhiFactory.updateArtSettings | 9 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| ramses-2024-10 | RamsesV3Pool._advancePeriod | 9 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| ramses-2024-10 | Position._updatePosition | 10 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| ramses-2024-10 | GaugeV3.cachePeriodEarned | 3 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| ramses-2024-10 | RamsesV3Pool.initialize | 6 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| ramses-2024-10 | Position.positionPeriodSecondsInRange | 8 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| ramses-2024-10 | RamsesV3Pool.swap | 1 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| secondswap-2024-12 | SecondSwap_Marketplace.doesFunctionExist | 5 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| vultisig-2024-06 | ILOManager.initialize | 5 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| vultisig-2024-06 | Multicall.multicall | 7 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| wildcat-2024-08 | WildcatMarket.borrow | 5 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| wildcat-2024-08 | WildcatMarket.closeMarket | 1 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| wildcat-2024-08 | WildcatMarket.repay | 6 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| wildcat-2024-08 | WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches | 2 |  | NEEDS_RUNTIME | source analysis exhausted: cross-contract / boundary value m |
| iq-ai-2025-01 | LiquidityManager.moveLiquidity | 3 | Y | SURVIVED | confirmed reproduced PoC — self-kill cannot kill a proven ex |
| kleidi-2024-10 | Timelock.checkCalldata | 10 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |
| munchables-2024-07 | LandManager.transferToUnoccupiedPlot | 44 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |
| phi-2024-08 | Cred._removeCredIdPerAddress | 33 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |
| phi-2024-08 | Cred.buyShareCredFor | 77 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |
| ramses-2024-10 | RamsesV3Pool.flash | 7 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |
| ramses-2024-10 | GaugeV3.getPeriodReward | 64 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |
| secondswap-2024-12 | SecondSwap_StepVesting.claimable | 3 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |
| secondswap-2024-12 | SecondSwap_Marketplace.spotPurchase | 16 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |
| secondswap-2024-12 | SecondSwap_StepVesting.transferVesting | 4 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |
| traitforge-2024-07 | EntityForging.forgeWithListed | 3 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |
| traitforge-2024-07 | TraitForgeNft.mintWithBudget | 5 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |
| vultisig-2024-06 | ILOPool.claim | 1 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |
| wildcat-2024-08 | WildcatMarketWithdrawals.executeWithdrawal | 24 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |
| wildcat-2024-08 | AccessControlHooks.grantRole | 75 | Y | SURVIVED | exploit thesis intact: source-backed consequence remains and |

## Reading
- KILLED requires a source-PROVABLE defense (dispositive guard, or full coverage with no consequence). Uncertainty is never a kill — it is NEEDS_RUNTIME / NEEDS_CONTEXT.
- Survivors are NOT validated/approved — only 'worth further investigation'.

