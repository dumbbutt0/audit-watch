# Sibling-Function Candidates — Phase 2 corpus mining

Discovered **1489** sibling candidate pairs across 16 subjects (in-scope, non-view, name-stem OR shared-call kinship). Top asymmetric candidates below; full machine list in `sibling_candidates.json`.

| Subject | Contract | A | B | kin | shared | jacc | only in A | only in B | req∆ | mod∆ |
|---|---|---|---|:--:|:--:|:--:|---|---|:--:|:--:|
| maia-talos | RootBridgeAgent | callOutAndBridge | callOutAndBridgeMultiple | Y | 9 | 0.64 | _createSettlement | _createMultipleSettlement,uint8 | 0 | - |
| zaros | CurveAdapter | executeSwapExactInputSingle | executeSwapExactInput | Y | 8 | 0.73 | — | decodePath | 0 | - |
| zaros | UniswapV2Adapter | executeSwapExactInputSingle | executeSwapExactInput | Y | 8 | 0.73 | — | decodePath | 0 | - |
| blackhole | RewardsDistributor | claim | claim_many | Y | 8 | 0.67 | getOriginalOwner,tokenIdToAVMId | — | -1 | - |
| beanstalk | EnrootFacet | enrootDeposit | enrootDeposits | Y | 7 | 0.33 | RemoveDeposit,addDepositToAccount,beanDenominatedValue,removeDepositFromAccount,stalkReward,stemTipForToken | _getTokenEnrootData,_removeDepositsFromAccount,addDepositAndCalculateStalk,div | 0 | - |
| zaros | UniswapV3Adapter | executeSwapExactInputSingle | executeSwapExactInput | Y | 6 | 0.46 | ExactInputSingleParams,calculateAmountOutMin,exactInputSingle | ExactInputParams,exactInput | 0 | - |
| maia-talos | ERC20Gauges | decrementGauge | decrementGauges | Y | 6 | 0.67 | — | SizeMismatchError | -1 | - |
| maia-talos | BranchBridgeAgent | callOutSignedAndBridge | callOutSignedAndBridgeMultiple | Y | 6 | 0.55 | _depositAndCall | _depositAndCallMultiple,uint8 | 0 | - |
| beanstalk | SiloFacet | withdrawDeposit | withdrawDeposits | Y | 5 | 0.56 | _withdrawDeposit | _withdrawDeposits | 0 | - |
| beanstalk | TokenSilo | _transferDeposit | _transferDeposits | Y | 5 | 0.24 | TransferSingle,_removeDepositFromAccount,checkForEarnedBeans,sub,transferGerminatingStalk,transferStalk | RemoveDeposits,TransferBatch,_getGerminationState,getGerminatingStem,removeDepositFromAccount,stalkReward | -1 | - |
| beanstalk | LibSiloPermit | permit | permits | Y | 5 | 0.62 | — | encodePacked | 0 | - |
| maia-talos | BranchBridgeAgent | _callOutAndBridge | _callOutAndBridgeMultiple | Y | 5 | 0.5 | _depositAndCall | _depositAndCallMultiple,uint8 | 0 | - |
| tokemak | LMPVaultRouterBase | deposit | _deposit | Y | 5 | 0.56 | _processEthIn,pullToken | MinSharesError,approve | -1 | - |
| beanstalk | MarketplaceFacet | transferPlot | transferPlots | Y | 4 | 0.36 | _cancelPodListing,_transferPlot,bytes32,validatePlotAndReturnPods | _transferPlots | -1 | - |
| beanstalk | MarketplaceFacet | transferPlot | _transferPlots | Y | 4 | 0.36 | _user,allowancePods,decrementAllowancePods,type | returns | 1 | Y |
| beanstalk | SiloFacet | transferDeposit | transferDeposits | Y | 4 | 0.44 | _transferDeposit | _transferDeposits,add | -2 | - |
| beanstalk | TokenSilo | _withdrawDeposit | _withdrawDeposits | Y | 4 | 0.44 | _removeDepositFromAccount | _removeDepositsFromAccount,returns | -1 | - |
| maia-talos | ERC20Gauges | incrementGauge | incrementGauges | Y | 4 | 0.57 | — | SizeMismatchError | -1 | - |
| maia-talos | BranchBridgeAgent | _createDepositSingle | _createDepositMultiple | Y | 4 | 0.5 | bridgeOut | bridgeOutMultiple | 0 | - |
| maia-talos | BranchBridgeAgentExecutor | executeWithSettlement | executeWithSettlementMultiple | Y | 4 | 0.21 | SettlementParams,anyExecuteSettlement,bytes20,bytes32,bytes4,clearToken | anyExecuteSettlementMultiple,bytes1,clearTokens,uint16,uint8 | 0 | - |
| hybra-finance | GaugeManager | createGauge | _createGauge | Y | 3 | 0.14 | — | GaugeCreated,ICLPool,IERC20,IGaugeFactory,IGaugeFactoryCL,IPairFactory | -9 | Y |
| hybra-finance | GaugeV2 | claimFees | _claimFees | Y | 3 | 0.3 | — | ClaimFees,IBribe,IERC20,IPair,notifyRewardAmount,safeApprove | 0 | Y |
| blackhole | address | getAmountOut | _getAmountOut | Y | 3 | 0.12 | IAlgebraCLFactory,IAlgebraPool,IPair,_createRoute,_getCLPoolAmountOut,_getPoolSwapRoutesFromThreeHop | IAlgebraPoolAPIStorage,QuoteExactInputSingleParams,getPoolAmountOut,quoteExactInputSingle | 0 | - |
| blackhole | GaugeManager | createGauge | _createGauge | Y | 3 | 0.15 | — | GaugeCreated,IERC20,IGaugeFactory,IGaugeFactoryCL,IPairFactory,IPairInfo | -9 | Y |
| blackhole | GaugeV2 | claimFees | _claimFees | Y | 3 | 0.3 | — | ClaimFees,IBribe,IERC20,IPair,notifyRewardAmount,safeApprove | 0 | Y |
| blackhole | RewardsDistributor | _claim | claim | Y | 3 | 0.19 | Claimed,balanceOfNFTAt,totalSupplyAtT,user_point_epoch,user_point_history | IERC20,deposit_for,getOriginalOwner,locked,ownerOf,tokenIdToAVMId | 3 | - |
| blackhole | RewardsDistributor | _claim | claim_many | Y | 3 | 0.21 | Claimed,balanceOfNFTAt,totalSupplyAtT,user_point_epoch,user_point_history | IERC20,deposit_for,locked,ownerOf,transfer | 2 | - |
| blackhole | RouterV2 | _addLiquidity | addLiquidity | Y | 3 | 0.2 | createPair,getPair,getReserves,quoteLiquidity | IBaseV1Pair,_safeTransferFrom,ensure,isGenesis,mint,pairFor | 1 | Y |
| maia-talos | BranchBridgeAgent | clearTokens | _clearToken | Y | 3 | 0.2 | SettlementMultipleParams,bytes1,bytes20,bytes32,bytes4,returns | — | 0 | Y |
| revert-lend | V3Vault | deposit | _deposit | Y | 2 | 0.12 | — | DailyLendIncreaseLimit,Deposit,GlobalLendLimit,IERC20,SignatureTransferDetails,_convertToAssets | -2 | - |
| revert-lend | V3Vault | withdraw | _withdraw | Y | 2 | 0.15 | — | IERC20,InsufficientLiquidity,Withdraw,_burn,_convertToAssets,_convertToShares | -1 | - |
| revert-lend | V3Vault | deposit | _deposit | Y | 2 | 0.12 | — | DailyLendIncreaseLimit,Deposit,GlobalLendLimit,IERC20,SignatureTransferDetails,_convertToAssets | -2 | - |
| revert-lend | V3Utils | swapAndMint | _swapAndMint | Y | 2 | 0.15 | SameToken,_prepareAddApproved,_prepareAddPermit2,decode | MintParams,SwapAndMint,_returnLeftoverTokens,_swapAndPrepareAmounts,mint,safeTransferFrom | 1 | - |
| hybra-finance | CLPool | collect | _collect | Y | 2 | 0.33 | — | Collect,get,safeTransfer | 0 | Y |
| hybra-finance | CLPool | collect | _collect | Y | 2 | 0.33 | — | Collect,get,safeTransfer | 0 | Y |
| hybra-finance | CLPool | burn | _burn | Y | 2 | 0.22 | — | Burn,ModifyPositionParams,_modifyPosition,int256,toInt128,uint128 | 0 | Y |
| hybra-finance | CLPool | burn | _burn | Y | 2 | 0.22 | — | Burn,ModifyPositionParams,_modifyPosition,int256,toInt128,uint128 | 0 | Y |
| hybra-finance | GaugeCL | claimFees | _claimFees | Y | 2 | 0.17 | — | ClaimFees,IBribe,IERC20,balanceOf,collectFees,notifyRewardAmount | 0 | Y |
| hybra-finance | GaugeManager | createGauges | createGauge | Y | 2 | 0.5 | — | — | 2 | - |
| hybra-finance | GaugeManager | createGauges | _createGauge | Y | 2 | 0.09 | — | GaugeCreated,ICLPool,IERC20,IGaugeFactory,IGaugeFactoryCL,IPairFactory | -7 | Y |
| hybra-finance | GaugeV2 | withdrawAll | _withdraw | Y | 2 | 0.25 | — | IRewarder,Withdraw,onReward,safeTransfer,updateReward | -3 | Y |
| hybra-finance | HYBR | _mint | mint | Y | 2 | 0.5 | Transfer | — | -1 | - |
| hybra-finance | HYBR | _transfer | transfer | Y | 2 | 0.5 | Transfer | — | 0 | - |
| hybra-finance | HYBR | burn | _burn | Y | 2 | 0.5 | — | Transfer | 0 | - |
| hybra-finance | VoterV3 | vote | _vote | Y | 2 | 0.12 | epochStart,isApprovedOrOwner,onlyNewEpoch | IBribe,Voted,_reset,balanceOfNFT,deposit,fetchExternalBribeFromPool | 1 | Y |
| hybra-finance | VotingEscrow | _create_lock | create_lock | Y | 2 | 0.4 | _deposit_for,_mint | — | 2 | Y |
| ark-project | Starklane | cancelRequest | _cancelRequest | Y | 2 | 0.22 | CancelRequestCompleted,IStarknetMessaging,cancelL1ToL2Message,requestDeserialize | _withdrawFromEscrow,collectionTypeFromHeader | 0 | - |
| beanstalk | FieldFacet | sow | _sow | Y | 2 | 0.22 | oneOutFlow,sowWithMin | _user,bean,burnToken,toUint128 | 0 | Y |
| beanstalk | FieldFacet | harvest | _harvest | Y | 2 | 0.22 | bean,oneOutFlow,sendToken | Harvest,_harvestPlot,returns | -1 | Y |
| beanstalk | ClaimFacet | claimPlenty | _claimPlenty | Y | 2 | 0.18 | getNonBeanTokenFromWell,oneOutFlow | ClaimPlenty,IWell,bean,isWell,sendToken,tokens | 0 | Y |
| beanstalk | ClaimFacet | plant | _plant | Y | 2 | 0.13 | _user | Plant,StalkBalanceChanged,_balanceOfEarnedBeans,_mow,add,addDepositToAccount | -1 | Y |
| beanstalk | LibSilo | _mow | __mow | Y | 2 | 0.22 | _lastUpdate,endAccountGermination,handleRainAndSops | _balanceOfGrownStalk,mintActiveStalk,stemTipForToken | 0 | - |
| beanstalk | Pipeline | pipe | _pipe | Y | 2 | 0.5 | — | checkReturn | 0 | - |
| beanstalk | Pipeline | advancedPipe | _advancedPipe | Y | 2 | 0.29 | — | _pipe,_pipeMem,getEthValue,useClipboard | 0 | - |
| blackhole | GaugeCL | claimFees | _claimFees | Y | 2 | 0.13 | — | ClaimFees,IBribe,IERC20,IGaugeFactoryCL,_safeTransfer,balanceOf | 0 | Y |
| blackhole | Black | _mint | mint | Y | 2 | 0.5 | Transfer | — | -1 | - |
| blackhole | Black | _transfer | transfer | Y | 2 | 0.5 | Transfer | — | 0 | - |
| blackhole | Black | burn | _burn | Y | 2 | 0.5 | — | Transfer | 0 | - |
| blackhole | GaugeManager | createGauges | createGauge | Y | 2 | 0.5 | — | — | 2 | - |
| blackhole | GaugeManager | createGauges | _createGauge | Y | 2 | 0.1 | — | GaugeCreated,IERC20,IGaugeFactory,IGaugeFactoryCL,IPairFactory,IPairInfo | -7 | Y |

## Summary
- total candidate pairs: **1489**
- asymmetric (a parity gap signal present): **984**
- name-stem siblings among asymmetric: **248** (the high-confidence tier)
- name-stem asymmetric by subject: maia-talos=75, blackhole=57, hybra-finance=37, tokemak=25, beanstalk=20, ethos-reserve=13, revert-lend=7, silo-finance=5, zaros=3, noya=3, ark-project=1, panoptic=1, recall=1
