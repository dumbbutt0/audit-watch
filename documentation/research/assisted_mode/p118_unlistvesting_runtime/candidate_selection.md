# P118 — Mechanical NOVEL candidate selection

**Rule:** corrected (permissionless-first, P115) ranking across all corpus subjects; exclude (a) confirmed positive
controls, (b) everything already run in P113/P114/P116, (c) the known-AWARDED set (for NOVELTY) = corpus
`awarded_findings` + memory (incl. phi H-03 `distribute`). Take the highest-scoring remaining PERMISSIONLESS function.
No manual cherry-picking.

**Excluded — already run (P113/P114/P116):** RamsesV3Pool.swap; WildcatMarket.closeMarket;
WildcatMarketWithdrawals.repayAndProcessUnpaidWithdrawalBatches; PhiNFT1155.claimFromFactory;
MigrationManager.burnRemainingPurchasedNFTs; CuratorRewardsDistributor.distribute (also awarded H-03);
MigrationManager.burnNFTs.

**Excluded — known awarded (novelty filter):** vultisig ILOPool.claim; munchables LandManager.transferToUnoccupiedPlot;
traitforge TraitForgeNft.mintWithBudget + EntityForging.forgeWithListed; phi Cred._removeCredIdPerAddress +
Cred.buyShareCredFor + CuratorRewardsDistributor.distribute(H-03); kleidi Timelock.checkCalldata; ramses
RamsesV3Pool.flash + GaugeV3.getPeriodReward; wildcat WildcatMarketWithdrawals.executeWithdrawal +
AccessControlHooks.grantRole; secondswap SecondSwap_StepVesting.transferVesting + .claimable +
SecondSwap_Marketplace.spotPurchase; iq-ai LiquidityManager.moveLiquidity.

**Top novel permissionless candidates (corrected ranking):**
1. **secondswap SecondSwap_Marketplace.unlistVesting — 2.9882  ← SELECTED**
2. ramses FeeCollector.collectProtocolFees — 2.9853
3. traitforge NukeFund.nuke — 2.9833
4. phi PhiFactory.claim — 2.9831
5. iq-ai AgentRouter.buy / .sell — 2.9608

**Selected: `secondswap-2024-12 :: SecondSwap_Marketplace.unlistVesting`** — novel (not in secondswap's awarded set
nor P97 memory). NB: it was ranked "permissionless" only because the actor_clarity role-guard regex
(`require(msg.sender==` / `only*`) misses the `seller == msg.sender` form (see source_trace.md) — a second
ranking-precision gap, distinct from P115's signature-modifier gap.
