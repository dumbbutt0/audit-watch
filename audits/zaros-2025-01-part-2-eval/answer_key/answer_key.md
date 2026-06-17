# Zaros Part 2 — Answer Key (CodeHawks final report, selected-for-report + validated)

Source: https://codehawks.cyfrin.io/c/2025-01-zaros-part-2/results?t=report (parsed from page payload, post-freeze)

Total: 70 findings — High 16, Medium 35, Low 19.

## [H-01] (High) Vaults weth reward is not distributed correctly
- Contracts: Collateral.sol, Constants.sol, CreditDelegation, CreditDelegationBranch, Distribution.sol, ERC4626.sol

## [H-02] (High) After an LP provider's initial stake, if they stake again in the same vault they lose all accumulated value from previous staked amount
- Contracts: EmptyDistribution, VaultRouterBranch, recalculateVault, wethRewardDistribution

## [H-03] (High) No one can redeem LP shares for reasonably high lockedCreditRatio and sufficiently high share distribution
- Contracts: Collateral.sol, Constants.sol, CreditDelegation, Distribution.sol, ERC20.sol, ERC20Mock.sol

## [H-04] (High) recalculateVaultsCreditCapacity() function always reverts after first redeem causing protocol DoS
- Contracts: CreditDelegation, NewCreditDelegation, PreviousCreditDelegation, RevertCreditDelegation, Vault.sol, VaultConfig

## [H-05] (High) settleVaultDebts will increase vaults' debt/credit instead of settling it
- Contracts: CreditDelegationBranch, dexAdapter, settleVault

## [H-06] (High) Incorrect calculation in CreditDelegationBranch::withdrawUsdTokenFromMarket allows attacker mint any amount of usdz
- Contracts: CreditDelegation, CreditDelegationBranch, LogWithdrawUsdTokenFromMarket, MarketMakingEngineConfiguration, PerpMarketCreditConfig, UsdToken

## [H-07] (High) `Market::getRealizedDebtUsd` calculates realized debt incorrectly
- Contracts: CreditDelegationBranch, Market.sol, MarketMakingEngineConfiguration, PerpsEngineConfigurationBranch, UsdToken, Vault.sol

## [H-08] (High) During _fillOrder with positive PnL, usdToken is minted less than trade account deposit amount
- Contracts: CreditDelegationBranch, IMarketMakingEngine, SettlementBranch, adjustedUsdToken, getAdjustedProfitForMarket, marketMakingEngine

## [H-09] (High) `rebalanceVaultsAssets` will always revert
- Contracts: InvalidVault, inCreditVault, inDebtVault, rebalanceVault

## [H-10] (High) Amount Of Asset Out Wrong Calculation
- Contracts: InsufficientVault, StabilityBranch, UsdTokenSwapConfig, indexToken

## [H-11] (High) Markets and vaults will not update their state until market fee is received, any deposits before market fee will not be reflected
- Contracts: Collateral.sol, Constants.sol, CreditDelegation, CreditDelegationBranch, ERC4626.sol, EnumerableMap.sol

## [H-12] (High) Incorrect WETH reward distribution in `FeeDistributionBranch.sol#_handleWethRewardDistribution()`
- Contracts: FeeDistributionBranch, MarketMakingEngine, WethRewardDistribution, handleWethRewardDistribution, receivedVault, testIncorrectWethDistribution

## [H-13] (High) Incorrect `AutoDeleverageFactor`.
- Contracts: CreditDelegationBranch, IMarketMakingEngine, Market.sol, SettlementBranch, getAdjustedProfitForMarket, marketMakingEngine

## [H-14] (High) LPs will not recieve their full amount of collateral on redeem
- Contracts: VaultRouterBranch, getIndexToken, getVault, indexToken, totalAssetsMinusVault

## [H-15] (High) Market-vault disconnection will bring permanent inconsistent state
- Contracts: Collateral.sol, Constants.sol, CreditDelegation, CreditDelegationBranch, ERC4626.sol, EnumerableMap.sol

## [H-16] (High) UsdTokenSwapConfig::Data::usdcAvailableForEngine Increases but Never Used, Locking USDC Forever
- Contracts: CreditDelegationBranch, StabilityBranch, UsdTokenSwapConfig, settleVault, usdcAvailableForEngine

## [M-01] (Medium) Incorrect Logic in MarketMakingEngineConfigurationBranch::configureFeeRecipient can cause DOS when attempting to change share value of an existing address
- Contracts: LogConfig, MarketMakingEngineConfiguration, MarketMakingEngineConfigurationBranch, marketMakingEngine, marketMakingEngineConfiguration

## [M-02] (Medium) Incorrect weight assignment in Vault::updateVaultAndCreditDelegationWeight leads to overleveraging vault positions and insolvency
- Contracts: CreditDelegation, CreditDelegationBranch, PerpMarketCreditConfig, TreeProxy, Utils.sol, VaultConfig

## [M-03] (Medium) rebalanceVaultsAssets incorrectly accounts vaults' depositedUsdc
- Contracts: BaseAdapter, CreditDelegationBranch, IDexAdapter, convertSd59x18ToToken, dexAdapter, inCreditVault

## [M-04] (Medium) `Market::configureConnectedVaults` Will Always Fail with Array Out of Bounds Error
- Contracts: Market.sol, MarketConfig, MarketHarness.sol, TreeProxy, Utils.sol, configureConnectedVault

## [M-05] (Medium) Staking design is not fair for users who staked earlier and longer
- Contracts: MarketEngine, VaultConfig, Vaults.sol, fundUserAndDepositInVault, fuzzVaultConfig, getPoCVaultConfig

## [M-06] (Medium) Stuck Funds
- Contracts: StabilityBranch

## [M-07] (Medium) FeeConversionKeeper.performUpkeep always reverts because of incorrect array management in checkUpkeep
- Contracts: FeeConversionKeeper, FeeDistributionBranch, IMarketMakingEngine, MarketMakingEngine, PerpMarketCreditConfig, checkFeeDistribution

## [M-08] (Medium) PremiumDiscountFactor Feature is Not Working
- Contracts: LogUpdateUsdTokenSwapConfig, MarketMakingEngineConfiguration, MarketMakingEngineConfigurationBranch, UsdTokenSwapConfig, configureUsdTokenSwapConfig

## [M-09] (Medium) Assets can be drained for vaults with LTV greater than certain threshold
- Contracts: MockVault, StabilityBranch, Test.sol, UD60x18.sol, UsdTokenSwapConfig, Vault.sol

## [M-10] (Medium) CreditDelegationBranch::settlevaultsdebt incorrectly swaps token from marketmakingengine and not directly from Zlpvault which breaks protocol intended functionality
- Contracts: ConvertMarket, CreditDelegationBranch, LogConvertMarket, MarketMakingEngine, MarketMakingEngineConfiguration, VaultRouterBranch

## [M-11] (Medium) Lack of credit capacity update from VaultRouterBranch::deposit causes DOS in CreditDelegationBranch::depositcreditformarket
- Contracts: CreditDelegation, CreditDelegationBranch, LogDepositCreditForMarket, MarketMakingEngineConfiguration, PerpMarketCreditConfig, PerpsEngineConfigurationBranch

## [M-12] (Medium) market's realized debt per vault share is not updated after clearing market's debt
- Contracts: Collateral.sol, Constants.sol, CreditDelegation, Distribution.sol, ERC20.sol, ERC20Mock.sol

## [M-13] (Medium) `_Ownable_init()` is not called in `MarketMakingEngineConfigurationBranch` contract
- Contracts: MarketMakingEngineConfigurationBranch, OwnableUpgradeable.sol, UpgradeBranch, createVault, testCreateVault

## [M-14] (Medium) CurveAdapter has cumulative slippage issue
- Contracts: CurveAdapter

## [M-15] (Medium) Negative Credit Capacity Handling Causes Complete Vault Lockout When Underwater
- Contracts: Math.sol, UnderwaterVault, VaultRouterBranch, convertSd59x18ToToken, ethVault, getIndexToken

## [M-16] (Medium) No Mechanism to Remove Fee Recipients Can Lead to Failed Reward Distributions
- Contracts: MarketMakingEngineConfiguration, MarketMakingEngineConfigurationBranch, marketMakingEngineConfiguration

## [M-17] (Medium) Vault accumulated values do not reflect market change correctly
- Contracts: Collateral.sol, Constants.sol, CreditDelegation, CreditDelegationBranch, ERC4626.sol, EnumerableMap.sol

## [M-18] (Medium) Adjusted profit will not use the current state of the system hence a use can withdraw all margins to bypass the profit adjustment
- Contracts: CreditDelegationBranch, IMarketMakingEngine, getAdjustedProfitForMarket, getConnectedVault, getCreditCapacityForMarket, marketMakingEngine

## [M-19] (Medium) CreditDelegationBranch Rebalancing Underflows When Debt Exceeds USDC Balance
- Contracts: Collateral.sol, CreditDelegationBranch, CreditDelegationBranchUnderflowVault, ERC20.sol, InvalidVault, MockMarketMakingEngine

## [M-20] (Medium) Incorrect Timestamp Usage in `StreamsLookup Revert`
- Contracts: MarketMakingEngine, UsdTokenSwapKeeper

## [M-21] (Medium) Issue with Decimal Offset Calculation Leading to Weak Donation Protection
- Contracts: VaultRouterBranch, Vaults.sol, ZlpVault, createZlpVault, indexToken, marketMakingEngine

## [M-22] (Medium) Mismatched slippage precision during deposit results in incorrect assertion of min-shares minted
- Contracts: VaultRouterBranch, convertToken, indexToken

## [M-23] (Medium) Share Minting and Redemption Attack
- Contracts: VaultRouterBranch, ZlpVault, totalAssetsMinusVault

## [M-24] (Medium) Unable to swap USD token to collateral for vaults in credit
- Contracts: MockVault, StabilityBranch, Test.sol, UD60x18.sol, UsdTokenSwapConfig, Vault.sol

## [M-25] (Medium) Vault credit capacity may not be correctly calculated
- Contracts: Market.sol, Vault.sol, VaultRouterBranch, connectedMarket, creditDelegation, distributeDebtToVault

## [M-26] (Medium) Wrong amount in calcaulation when performing a swap from vault asset to usdc
- Contracts: IDexAdapter, IPriceAdapter, MarketMakingEngineConfiguration, SettleVault, convertSd59x18ToToken, convertToken

## [M-27] (Medium) `checkFeeDistributionNeeded` Will Not Work With Low Decimal Assets
- Contracts: FeeConversionKeeper, FeeDistributionBranch, checkFeeDistribution, convertToken, convertUd60x18ToToken, getFeeConversionKeeper

## [M-28] (Medium) CreditDelegationBranch::depositCreditForMarket cannot update market realized debt properly
- Contracts: CreditDelegationBranch, depositCreditForMarket, distributeDebtToVault, realizedDebtUsdPerVault, recalculateConnectedMarket, recalculateVault

## [M-29] (Medium) Decimal Precision Mismatch Causing Incorrect Swap Reverts in `StabilityBranch.initiateSwap()`
- Contracts: Collateral.sol, IERC20Metadata.sol, IERC4626.sol, IPriceAdapter, InsufficientVault, Math.sol

## [M-30] (Medium) Duplicate `Collateral.Data` struct causes admin configuration conflict
- Contracts: Collateral.sol, MarketMakingEngineConfigurationBranch, StabilityBranch, Vault.sol, VaultRouterBranch, getVault

## [M-31] (Medium) FeeConversionKeeper::performUpkeep May Exceed Gas Limit Due to Vault Updates
- Contracts: FeeConversionKeeper, FeeDistributionBranch, PerpMarketCreditConfig, configureFeeConversionKeeper, convertUd60x18ToToken, expectedToken

## [M-32] (Medium) The `settleCreditDeposit` function is incorrect.
- Contracts: Market.sol, Vault.sol, connectedMarket, creditDelegation, distributeDebtToVault, getVault

## [M-33] (Medium) Usd token can be overwithdrawn from market
- Contracts: Collateral.sol, Constants.sol, CreditDelegation, CreditDelegationBranch, DexSwapStrategy.sol, Distribution.sol

## [M-34] (Medium) Vault's total credit capacity keeps changing when being recalculated even though there is no market activity
- Contracts: Collateral.sol, Constants.sol, CreditDelegation, CreditDelegationBranch, ERC4626.sol, EnumerableMap.sol

## [M-35] (Medium) Wrong values of newly added `vault`
- Contracts: CreditDelegation, lastVault, wethRewardPerVault

## [L-01] (Low) Low issues collection
- Contracts: CreditDelegationBranch, CurveAdapter, Market.sol, MarketMakingEngineConfigurationBranch, StabilityBranch, UsdToken

## [L-02] (Low) Users Guaranteed To Lose Base Fees When Initiating Swaps on Non-Live Vaults
- Contracts: StabilityBranch, currentVault, initialVault

## [L-03] (Low) Anyone can call `BaseAdapter::__BaseAdapter_init` function because the function has `initializer` modifier instead of `onlyInitializing`
- Contracts: BaseAdapter, CurveAdapter, Initializable.sol, UniswapV2Adapter, UniswapV3Adapter, bAdapter

## [L-04] (Low) Low issues collection
- Contracts: CreditDelegationBranch, CurveAdapter, Market.sol, MarketMakingEngineConfigurationBranch, StabilityBranch, UsdToken

## [L-05] (Low) Total debt used in fulfiling swap actions is wrong because we did not update the vault.
- Contracts: InsufficientVault, MarketMakingEngineConfiguration, StabilityConfiguration, UsdToken, UsdTokenSwapConfig, connectedMarket

## [L-06] (Low) Custom Referral Code Conflict Across Engines
- Contracts: ERC1967Proxy, Referral.sol, Test.sol, configureEngine

## [L-07] (Low) Lack of an update of the pool state will cause Initiate Swap to return an incorrect Amountout
- Contracts: InsufficientVault, MarketMakingEngineConfiguration, UsdTokenSwapConfig, connectedMarket, currentVault, indexToken

## [L-08] (Low) Missing ERC-20 Metadata in ZlpVault (EIP-4626 Violation)
- Contracts: ZlpVault

## [L-09] (Low) Protocol uses CurveRegistryExchange which is outdated
- Contracts: CurveAdapter, ICurveSwapRouter.sol, fromToken, toToken

## [L-10] (Low) Chainlink Oracle incompatibilities
- Contracts: AccountNFT.sol, IPriceAdapter, priceAdapter

## [L-11] (Low) Incorrect Array Length Parameters in Error Message for Deposit and Redeem Fees Validation
- Contracts: MarketMakingEngineConfigurationBranch

## [L-12] (Low) Chainlink Keeper Cannot Process All Swap Logs in a Block
- Contracts: StabilityBranch, UsdTokenSwapKeeper

## [L-13] (Low) High Severity - Incorrect Timestamp Validation at `StabilityConfiguration` (Stale Price Reports)
- Contracts: StabilityConfiguration

## [L-14] (Low) Invalid referral data retrieval
- Contracts: Referral.sol, ReferralConfiguration, VaultRouterBranch, referralConfiguration

## [L-15] (Low) Users can initiate multiple swaps against the same vault/collateral causing the users to lntiate swaps that can not be fulfillable.
- Contracts: InsufficientVault, MarketMakingEngineConfiguration, UsdTokenSwapConfig, ZeroOutputToken, currentVault, indexToken

## [L-16] (Low) Users could potentially use their own referral code
- Contracts: Referral.sol, TradingAccountBranch, VaultRouterBranch, givenTheTradingAccountToken, perpsEngine, t.sol

## [L-17] (Low) VaultRouterBranch::getVaultCreditCapacity does not take zero return into account
- Contracts: VaultRouterBranch, convertSd59x18ToToken, getIndexToken, getVault, indexToken, totalAssetsMinusVault

## [L-18] (Low) Whitelisted users can create trading accounts for non-whitelisted users
- Contracts: LogCancelMarket, OrderBranch, PerpsEngineConfiguration, TradingAccountBranch, Whitelist.sol, givenTheTradingAccountToken

## [L-19] (Low) wrong value emitted in `LogLiquidateAccount` event
- Contracts: LiquidationBranch, activeMarket
