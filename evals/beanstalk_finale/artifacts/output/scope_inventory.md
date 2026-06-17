# Scope Inventory

Contract path: `contracts/2024-05-beanstalk-the-finale/protocol/contracts`
Files: 219  |  Total LOC: 30,805

| File | LOC | External Imports |
|---|---|---|
| `C.sol` | 175 | — |
| `beanstalk/Diamond.sol` | 54 | — |
| `beanstalk/Invariable.sol` | 199 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibRedundantMathSigned256.sol, contracts/C.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/storage/System.sol, contracts/libraries/LibAppStorage.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/libraries/LibUnripe.sol, contracts/libraries/Silo/LibSilo.sol, contracts/beanstalk/sun/SeasonFacet/Weather.sol |
| `beanstalk/ReentrancyGuard.sol` | 24 | — |
| `beanstalk/barn/FertilizerFacet.sol` | 253 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/C.sol, contracts/beanstalk/Invariable.sol, contracts/libraries/LibTractor.sol, contracts/libraries/LibDiamond.sol, contracts/interfaces/IFertilizer.sol, contracts/libraries/LibBarnRaise.sol, contracts/libraries/LibFertilizer.sol, contracts/libraries/Token/LibTransfer.sol, contracts/libraries/Oracle/LibUsdOracle.sol, contracts/libraries/LibRedundantMath128.sol, contracts/libraries/LibRedundantMath256.sol |
| `beanstalk/barn/UnripeFacet.sol` | 347 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol, contracts/C.sol, contracts/interfaces/IBean.sol, contracts/libraries/LibChop.sol, contracts/libraries/LibUnripe.sol, contracts/libraries/Well/LibWell.sol, contracts/beanstalk/Invariable.sol, contracts/libraries/LibDiamond.sol, contracts/libraries/LibTractor.sol, contracts/libraries/LibBarnRaise.sol, contracts/libraries/Token/LibTransfer.sol, contracts/beanstalk/ReentrancyGuard.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibLockedUnderlying.sol |
| `beanstalk/diamond/DiamondCutFacet.sol` | 30 | ⚠️ contracts/interfaces/IDiamondCut.sol, contracts/libraries/LibDiamond.sol, contracts/beanstalk/Invariable.sol |
| `beanstalk/diamond/DiamondLoupeFacet.sol` | 73 | ⚠️ @openzeppelin/contracts/utils/introspection/IERC165.sol, contracts/libraries/LibDiamond.sol, contracts/interfaces/IDiamondLoupe.sol |
| `beanstalk/diamond/OwnershipFacet.sol` | 31 | ⚠️ contracts/libraries/LibDiamond.sol |
| `beanstalk/diamond/PauseFacet.sol` | 44 | ⚠️ contracts/libraries/LibDiamond.sol, contracts/libraries/LibRedundantMath256.sol |
| `beanstalk/farm/DepotFacet.sol` | 84 | ⚠️ contracts/interfaces/IPipeline.sol, contracts/libraries/LibFunction.sol, contracts/libraries/Token/LibEth.sol, contracts/beanstalk/Invariable.sol |
| `beanstalk/farm/FarmFacet.sol` | 63 | ⚠️ contracts/beanstalk/Invariable.sol |
| `beanstalk/farm/TokenFacet.sol` | 335 | ⚠️ contracts/libraries/Token/LibTransfer.sol, contracts/libraries/Token/LibWeth.sol, contracts/libraries/Token/LibEth.sol, contracts/libraries/Token/LibTokenPermit.sol, contracts/libraries/Token/LibTokenApprove.sol, contracts/libraries/LibTractor.sol, contracts/interfaces/IERC1155Receiver.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/Invariable.sol |
| `beanstalk/farm/TokenSupportFacet.sol` | 106 | ⚠️ @openzeppelin/contracts/token/ERC1155/IERC1155.sol, @openzeppelin/contracts/token/ERC721/IERC721.sol, @openzeppelin/contracts/token/ERC20/extensions/IERC20Permit.sol, contracts/beanstalk/Invariable.sol |
| `beanstalk/farm/TractorFacet.sol` | 175 | ⚠️ @openzeppelin/contracts/utils/cryptography/ECDSA.sol, @openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibBytes.sol |
| `beanstalk/field/FieldFacet.sol` | 452 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/C.sol, contracts/libraries/LibRedundantMath32.sol, contracts/libraries/LibRedundantMath128.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibTractor.sol, contracts/libraries/Token/LibTransfer.sol, contracts/libraries/LibDibbler.sol, contracts/beanstalk/Invariable.sol, contracts/libraries/LibDiamond.sol, contracts/libraries/LibMarket.sol |
| `beanstalk/init/InitDiamond.sol` | 71 | ⚠️ @openzeppelin/contracts/utils/introspection/IERC165.sol, @openzeppelin/contracts/token/ERC1155/IERC1155.sol, contracts/libraries/LibGauge.sol, contracts/beanstalk/sun/SeasonFacet/Weather.sol, contracts/libraries/LibIncentive.sol |
| `beanstalk/init/InitDistribution.sol` | 67 | ⚠️ contracts/C.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/storage/System.sol, contracts/ecosystem/ShipmentPlanner.sol |
| `beanstalk/init/InitEmpty.sol` | 13 | — |
| `beanstalk/init/InitInvariants.sol` | 38 | ⚠️ @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/C.sol, contracts/libraries/LibDiamond.sol |
| `beanstalk/init/InitMint.sol` | 17 | — |
| `beanstalk/init/InitReseed.sol` | 39 | ⚠️ contracts/beanstalk/storage/AppStorage.sol, contracts/C.sol, contracts/libraries/LibTractor.sol, contracts/libraries/LibDiamond.sol |
| `beanstalk/init/InitSiloToken.sol` | 20 | — |
| `beanstalk/init/InitWhitelist.sol` | 55 | ⚠️ contracts/libraries/Silo/LibLegacyWhitelist.sol, contracts/beanstalk/silo/BDVFacet.sol |
| `beanstalk/init/InitWhitelistStatuses.sol` | 38 | ⚠️ contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/C.sol |
| `beanstalk/init/InitalizeDiamond.sol` | 275 | ⚠️ contracts/beanstalk/sun/LiquidityWeightFacet.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/storage/System.sol, contracts/beanstalk/sun/GaugePointFacet.sol, contracts/libraries/LibTractor.sol, contracts/libraries/LibDiamond.sol, contracts/libraries/LibCases.sol, contracts/libraries/LibGauge.sol, contracts/beanstalk/silo/BDVFacet.sol, contracts/libraries/LibUnripe.sol, contracts/C.sol |
| `beanstalk/init/newInitDiamond.sol` | 26 | ⚠️ contracts/beanstalk/init/InitalizeDiamond.sol, contracts/C.sol |
| `beanstalk/init/reseed/L1/ReseedL2Migration.sol` | 49 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/beanstalk/migration/L1AppStorage.sol, contracts/C.sol |
| `beanstalk/init/reseed/L2/ReseedBarn.sol` | 97 | ⚠️ @openzeppelin/contracts/proxy/transparent/TransparentUpgradeableProxy.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/tokens/Fertilizer/Fertilizer.sol, contracts/C.sol |
| `beanstalk/init/reseed/L2/ReseedBean.sol` | 237 | ⚠️ @openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol, @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/tokens/ERC20/BeanstalkERC20.sol, contracts/interfaces/basin/IWell.sol, contracts/libraries/Well/LibWell.sol, contracts/C.sol |
| `beanstalk/init/reseed/L2/ReseedField.sol` | 73 | ⚠️ contracts/beanstalk/storage/AppStorage.sol, contracts/C.sol |
| `beanstalk/init/reseed/L2/ReseedInternalBalances.sol` | 65 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/C.sol |
| `beanstalk/init/reseed/L2/ReseedSilo.sol` | 181 | ⚠️ contracts/beanstalk/storage/AppStorage.sol, contracts/libraries/Silo/LibTokenSilo.sol, contracts/libraries/LibBytes.sol, contracts/C.sol |
| `beanstalk/init/reseed/L2/ReseedSun.sol` | 57 | ⚠️ contracts/beanstalk/storage/AppStorage.sol, contracts/libraries/LibCases.sol, contracts/C.sol |
| `beanstalk/init/reseed/L2/ReseedWhitelist.sol` | 40 | ⚠️ contracts/beanstalk/storage/AppStorage.sol, contracts/libraries/Silo/LibWhitelist.sol, contracts/beanstalk/storage/System.sol, contracts/C.sol |
| `beanstalk/market/MarketplaceFacet/Listing.sol` | 190 | ⚠️ contracts/libraries/Token/LibTransfer.sol, contracts/libraries/LibMarket.sol |
| `beanstalk/market/MarketplaceFacet/MarketplaceFacet.sol` | 214 | ⚠️ contracts/beanstalk/Invariable.sol, contracts/C.sol, contracts/libraries/LibTractor.sol, contracts/libraries/Token/LibTransfer.sol, contracts/libraries/LibMarket.sol |
| `beanstalk/market/MarketplaceFacet/Order.sol` | 158 | ⚠️ contracts/C.sol, contracts/libraries/Token/LibTransfer.sol, contracts/libraries/LibMarket.sol |
| `beanstalk/market/MarketplaceFacet/PodTransfer.sol` | 110 | ⚠️ contracts/beanstalk/ReentrancyGuard.sol, contracts/libraries/LibDibbler.sol, contracts/C.sol |
| `beanstalk/metadata/MetadataFacet.sol` | 92 | ⚠️ @openzeppelin/contracts/utils/Strings.sol, contracts/libraries/LibBytes.sol, contracts/libraries/Silo/LibTokenSilo.sol |
| `beanstalk/metadata/MetadataImage.sol` | 664 | ⚠️ @openzeppelin/contracts/utils/Strings.sol, @openzeppelin/contracts/token/ERC20/ERC20.sol, contracts/libraries/LibBytes64.sol, contracts/libraries/LibRedundantMath256.sol |
| `beanstalk/migration/BeanL1RecieverFacet.sol` | 45 | ⚠️ contracts/C.sol |
| `beanstalk/migration/BeanL2MigrationFacet.sol` | 58 | ⚠️ contracts/C.sol, contracts/beanstalk/Invariable.sol |
| `beanstalk/migration/L1AppStorage.sol` | 634 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/interfaces/IDiamondCut.sol |
| `beanstalk/migration/L1Libraries/LibBalance.sol` | 101 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol, @openzeppelin/contracts/utils/math/Math.sol, @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/libraries/LibRedundantMath256.sol |
| `beanstalk/migration/L1Libraries/LibEth.sol` | 23 | — |
| `beanstalk/migration/L1Libraries/LibL1AppStorage.sol` | 20 | — |
| `beanstalk/migration/L1Libraries/LibTokenApprove.sol` | 43 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol |
| `beanstalk/migration/L1Libraries/LibTransfer.sol` | 103 | ⚠️ @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol, contracts/libraries/LibRedundantMath256.sol, contracts/interfaces/IBean.sol |
| `beanstalk/migration/L1Libraries/LibWeth.sol` | 37 | ⚠️ contracts/interfaces/IWETH.sol, contracts/beanstalk/migration/L1Libraries/LibTransfer.sol |
| `beanstalk/migration/L1ReentrancyGuard.sol` | 24 | — |
| `beanstalk/migration/L1TokenFacet.sol` | 322 | ⚠️ contracts/interfaces/IERC1155Receiver.sol, contracts/beanstalk/migration/L1Libraries/LibTransfer.sol, contracts/beanstalk/migration/L1Libraries/LibWeth.sol, contracts/beanstalk/migration/L1Libraries/LibEth.sol, contracts/beanstalk/migration/L1Libraries/LibTokenApprove.sol, contracts/beanstalk/migration/L1AppStorage.sol, contracts/beanstalk/migration/L1ReentrancyGuard.sol, contracts/libraries/LibRedundantMath256.sol, contracts/C.sol |
| `beanstalk/silo/ApprovalFacet.sol` | 200 | ⚠️ contracts/C.sol, contracts/libraries/Silo/LibSilo.sol, contracts/libraries/Silo/LibTokenSilo.sol, contracts/libraries/Silo/LibSiloPermit.sol, contracts/libraries/LibRedundantMath32.sol, contracts/libraries/Convert/LibConvert.sol, contracts/beanstalk/Invariable.sol, contracts/libraries/LibTractor.sol |
| `beanstalk/silo/BDVFacet.sol` | 57 | ⚠️ contracts/C.sol, contracts/libraries/LibUnripe.sol, contracts/libraries/Well/LibWellBdv.sol, contracts/libraries/LibBarnRaise.sol |
| `beanstalk/silo/ConvertFacet.sol` | 105 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/C.sol, contracts/libraries/LibTractor.sol, contracts/libraries/Silo/LibSilo.sol, contracts/libraries/Silo/LibTokenSilo.sol, contracts/libraries/LibRedundantMath32.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/Convert/LibConvert.sol, contracts/libraries/Convert/LibConvertData.sol, contracts/beanstalk/Invariable.sol, contracts/libraries/LibRedundantMathSigned256.sol, contracts/libraries/Convert/LibPipelineConvert.sol |
| `beanstalk/silo/ConvertGettersFacet.sol` | 130 | ⚠️ contracts/libraries/LibAppStorage.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/Convert/LibConvert.sol, contracts/libraries/Minting/LibWellMinting.sol, contracts/libraries/Oracle/LibDeltaB.sol |
| `beanstalk/silo/EnrootFacet.sol` | 260 | ⚠️ contracts/libraries/Silo/LibSilo.sol, contracts/libraries/Silo/LibTokenSilo.sol, contracts/libraries/LibRedundantMath32.sol, contracts/libraries/LibTractor.sol, contracts/beanstalk/Invariable.sol |
| `beanstalk/silo/L2ContractMigrationFacet.sol` | 242 | ⚠️ @openzeppelin/contracts/utils/cryptography/MerkleProof.sol, @openzeppelin/contracts/utils/cryptography/ECDSA.sol, contracts/C.sol, contracts/beanstalk/ReentrancyGuard.sol, contracts/libraries/LibBytes.sol, contracts/libraries/Silo/LibTokenSilo.sol, contracts/beanstalk/Invariable.sol |
| `beanstalk/silo/PipelineConvertFacet.sol` | 111 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/C.sol, contracts/libraries/LibTractor.sol, contracts/libraries/Silo/LibSilo.sol, contracts/libraries/Silo/LibTokenSilo.sol, contracts/libraries/LibRedundantMath32.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/Convert/LibConvert.sol, contracts/libraries/Well/LibWell.sol, contracts/libraries/Convert/LibConvertData.sol, contracts/beanstalk/Invariable.sol, contracts/libraries/LibRedundantMathSigned256.sol, contracts/libraries/Convert/LibPipelineConvert.sol, contracts/libraries/Oracle/LibDeltaB.sol |
| `beanstalk/silo/SiloFacet/ClaimFacet.sol` | 206 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/C.sol, contracts/libraries/Silo/LibSilo.sol, contracts/beanstalk/Invariable.sol, contracts/libraries/LibTractor.sol, contracts/libraries/Well/LibWell.sol, contracts/libraries/Token/LibTransfer.sol, contracts/libraries/Silo/LibTokenSilo.sol, contracts/beanstalk/ReentrancyGuard.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol |
| `beanstalk/silo/SiloFacet/SiloFacet.sol` | 257 | ⚠️ contracts/libraries/Silo/LibSiloPermit.sol, contracts/beanstalk/Invariable.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol |
| `beanstalk/silo/SiloFacet/SiloGettersFacet.sol` | 599 | ⚠️ contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/storage/Account.sol, contracts/beanstalk/storage/System.sol, contracts/libraries/LibRedundantMath128.sol, contracts/libraries/Silo/LibGerminate.sol, contracts/beanstalk/ReentrancyGuard.sol, contracts/libraries/Silo/LibTokenSilo.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibBytes.sol, contracts/libraries/Silo/LibSilo.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/C.sol, contracts/libraries/Silo/LibFlood.sol |
| `beanstalk/silo/SiloFacet/TokenSilo.sol` | 497 | ⚠️ @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol, @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/C.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/storage/System.sol, contracts/beanstalk/ReentrancyGuard.sol, contracts/libraries/LibRedundantMath128.sol, contracts/libraries/LibRedundantMath32.sol, contracts/libraries/Silo/LibGerminate.sol, contracts/libraries/Silo/LibTokenSilo.sol, contracts/libraries/Silo/LibSilo.sol, contracts/libraries/LibTractor.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibBytes.sol, contracts/libraries/Token/LibTransfer.sol |
| `beanstalk/silo/WhitelistFacet/WhitelistFacet.sol` | 247 | ⚠️ contracts/libraries/LibDiamond.sol, contracts/libraries/Silo/LibWhitelist.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/silo/WhitelistFacet/WhitelistedTokens.sol, contracts/beanstalk/Invariable.sol, contracts/beanstalk/ReentrancyGuard.sol, contracts/beanstalk/storage/System.sol |
| `beanstalk/silo/WhitelistFacet/WhitelistedTokens.sol` | 65 | ⚠️ contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/beanstalk/storage/System.sol |
| `beanstalk/storage/Account.sol` | 125 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol |
| `beanstalk/storage/AppStorage.sol` | 23 | — |
| `beanstalk/storage/System.sol` | 438 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol |
| `beanstalk/sun/GaugePointFacet.sol` | 69 | ⚠️ contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibGauge.sol |
| `beanstalk/sun/LiquidityWeightFacet.sol` | 22 | — |
| `beanstalk/sun/OracleFacet.sol` | 42 | ⚠️ contracts/beanstalk/Invariable.sol, contracts/beanstalk/ReentrancyGuard.sol, contracts/libraries/Oracle/LibUsdOracle.sol |
| `beanstalk/sun/SeasonFacet/Distribution.sol` | 48 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/C.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/storage/System.sol, contracts/libraries/LibDiamond.sol, contracts/beanstalk/ReentrancyGuard.sol |
| `beanstalk/sun/SeasonFacet/Oracle.sol` | 28 | ⚠️ contracts/C.sol, contracts/beanstalk/ReentrancyGuard.sol, contracts/libraries/Minting/LibWellMinting.sol, contracts/libraries/LibRedundantMathSigned256.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol |
| `beanstalk/sun/SeasonFacet/SeasonFacet.sol` | 111 | ⚠️ contracts/libraries/LibIncentive.sol, contracts/libraries/Token/LibTransfer.sol, contracts/libraries/Well/LibWell.sol, contracts/libraries/LibGauge.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/libraries/Silo/LibGerminate.sol, contracts/beanstalk/Invariable.sol, contracts/libraries/LibTractor.sol, contracts/libraries/LibRedundantMath256.sol |
| `beanstalk/sun/SeasonFacet/SeasonGettersFacet.sol` | 489 | ⚠️ contracts/libraries/Decimal.sol, contracts/libraries/LibEvaluate.sol, contracts/libraries/Oracle/LibUsdOracle.sol, contracts/libraries/Minting/LibWellMinting.sol, contracts/libraries/Well/LibWell.sol, contracts/libraries/LibRedundantMathSigned256.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/libraries/LibGauge.sol, contracts/libraries/LibCases.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/Oracle/LibDeltaB.sol, contracts/libraries/Silo/LibFlood.sol, contracts/libraries/Silo/LibGerminate.sol |
| `beanstalk/sun/SeasonFacet/Sun.sol` | 85 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/libraries/LibRedundantMath128.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibShipping.sol |
| `beanstalk/sun/SeasonFacet/Weather.sol` | 179 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/libraries/LibEvaluate.sol, contracts/libraries/LibRedundantMath128.sol, contracts/libraries/LibCases.sol, contracts/interfaces/basin/IBeanstalkWellFunction.sol, contracts/libraries/Well/LibWell.sol, contracts/interfaces/basin/IWell.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/libraries/Minting/LibWellMinting.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibRedundantMathSigned256.sol, contracts/libraries/LibAppStorage.sol, contracts/libraries/Oracle/LibDeltaB.sol, contracts/libraries/Silo/LibFlood.sol |
| `ecosystem/Drafter.sol` | 48 | ⚠️ contracts/libraries/LibClipboard.sol, contracts/libraries/LibBytes.sol |
| `ecosystem/ShipmentPlanner.sol` | 83 | — |
| `ecosystem/junction/Junction.sol` | 14 | — |
| `ecosystem/junction/LogicJunction.sol` | 43 | — |
| `ecosystem/junction/MathJunction.sol` | 37 | — |
| `ecosystem/oracles/UsdOracle.sol` | 63 | ⚠️ contracts/libraries/Oracle/LibUsdOracle.sol, contracts/libraries/Oracle/LibWstethEthOracle.sol |
| `ecosystem/price/BeanstalkPrice.sol` | 51 | ⚠️ contracts/libraries/LibRedundantMath256.sol |
| `ecosystem/price/P.sol` | 24 | — |
| `ecosystem/price/WellPrice.sol` | 102 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/libraries/LibRedundantMath256.sol |
| `interfaces/IBean.sol` | 17 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol |
| `interfaces/IBeanstalk.sol` | 110 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol |
| `interfaces/IBeanstalkTransfer.sol` | 75 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol |
| `interfaces/IDelegation.sol` | 7 | — |
| `interfaces/IDiamondCut.sol` | 34 | — |
| `interfaces/IDiamondLoupe.sol` | 35 | — |
| `interfaces/IERC1155Receiver.sol` | 58 | — |
| `interfaces/IERC4494.sol` | 28 | ⚠️ @openzeppelin/contracts/utils/introspection/IERC165.sol |
| `interfaces/IFertilizer.sol` | 30 | — |
| `interfaces/ILegacySilo.sol` | 8 | — |
| `interfaces/IMockFBeanstalk.sol` | 1,894 | — |
| `interfaces/IPipeline.sol` | 40 | — |
| `interfaces/IProxyAdmin.sol` | 6 | — |
| `interfaces/IQuoter.sol` | 57 | — |
| `interfaces/IShipmentPlanner.sol` | 15 | ⚠️ contracts/ecosystem/ShipmentPlanner.sol |
| `interfaces/ISwapRouter.sol` | 33 | — |
| `interfaces/IUSDC.sol` | 17 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol |
| `interfaces/IWETH.sol` | 16 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol |
| `interfaces/basin/IAquifer.sol` | 55 | ⚠️ @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol |
| `interfaces/basin/IBeanstalkWellFunction.sol` | 49 | — |
| `interfaces/basin/IWell.sol` | 430 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol |
| `interfaces/basin/IWellFunction.sol` | 68 | — |
| `interfaces/basin/pumps/ICappedReservesPump.sol` | 16 | — |
| `interfaces/basin/pumps/ICumulativePump.sol` | 37 | — |
| `interfaces/basin/pumps/IInstantaneousPump.sol` | 18 | — |
| `interfaces/basin/pumps/IPump.sol` | 20 | — |
| `interfaces/chainlink/IChainlinkAggregator.sol` | 37 | — |
| `libraries/Convert/LibChopConvert.sol` | 49 | ⚠️ contracts/libraries/LibChop.sol, contracts/libraries/LibUnripe.sol, contracts/C.sol, contracts/interfaces/IBean.sol |
| `libraries/Convert/LibConvert.sol` | 572 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/Well/LibWell.sol, contracts/libraries/LibBarnRaise.sol, contracts/libraries/LibAppStorage.sol, contracts/libraries/Minting/LibWellMinting.sol, contracts/C.sol, contracts/libraries/LibRedundantMathSigned256.sol, contracts/libraries/Oracle/LibDeltaB.sol, contracts/beanstalk/storage/System.sol, contracts/libraries/Silo/LibSilo.sol, contracts/libraries/LibTractor.sol, contracts/libraries/Silo/LibGerminate.sol, contracts/libraries/Silo/LibTokenSilo.sol, contracts/libraries/LibBytes.sol |
| `libraries/Convert/LibConvertData.sol` | 50 | — |
| `libraries/Convert/LibLambdaConvert.sol` | 25 | — |
| `libraries/Convert/LibPipelineConvert.sol` | 215 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/C.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/libraries/Oracle/LibDeltaB.sol, contracts/interfaces/IPipeline.sol, contracts/libraries/Convert/LibConvertData.sol, contracts/libraries/LibTractor.sol, contracts/libraries/Silo/LibTokenSilo.sol |
| `libraries/Convert/LibUnripeConvert.sol` | 113 | ⚠️ contracts/C.sol, contracts/interfaces/IBean.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibBarnRaise.sol |
| `libraries/Convert/LibWellConvert.sol` | 188 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/Convert/LibConvertData.sol, contracts/libraries/Well/LibWell.sol, contracts/C.sol, contracts/interfaces/basin/IWell.sol, contracts/interfaces/basin/IBeanstalkWellFunction.sol, contracts/beanstalk/silo/ConvertFacet.sol |
| `libraries/Decimal.sol` | 159 | ⚠️ contracts/libraries/LibRedundantMath256.sol |
| `libraries/LibAppStorage.sol` | 19 | — |
| `libraries/LibBarnRaise.sol` | 28 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/interfaces/basin/IWell.sol, contracts/C.sol, contracts/libraries/LibAppStorage.sol |
| `libraries/LibBytes.sol` | 269 | ⚠️ contracts/C.sol |
| `libraries/LibBytes64.sol` | 92 | — |
| `libraries/LibCases.sol` | 268 | — |
| `libraries/LibChop.sol` | 37 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/libraries/LibUnripe.sol, contracts/interfaces/IBean.sol, contracts/libraries/LibRedundantMath256.sol |
| `libraries/LibClipboard.sol` | 114 | — |
| `libraries/LibDiamond.sol` | 296 | ⚠️ @openzeppelin/contracts/utils/introspection/IERC165.sol |
| `libraries/LibDibbler.sol` | 420 | ⚠️ @openzeppelin/contracts/utils/math/Math.sol, @prb/math/contracts/PRBMath.sol, contracts/libraries/LibPRBMathRoundable.sol, contracts/beanstalk/storage/Account.sol, contracts/libraries/LibRedundantMath256.sol |
| `libraries/LibEvaluate.sol` | 371 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/libraries/Decimal.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/libraries/LibUnripe.sol, contracts/libraries/LibRedundantMath32.sol, contracts/libraries/Well/LibWell.sol, contracts/libraries/LibBarnRaise.sol, contracts/libraries/LibRedundantMath256.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/libraries/LibAppStorage.sol, contracts/beanstalk/storage/System.sol |
| `libraries/LibFarm.sol` | 75 | — |
| `libraries/LibFertilizer.sol` | 263 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, @openzeppelin/contracts/utils/math/SafeCast.sol, @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol, contracts/libraries/LibRedundantMath256.sol, contracts/interfaces/basin/IWell.sol, contracts/libraries/LibDiamond.sol, contracts/libraries/Well/LibWell.sol, contracts/libraries/Oracle/LibUsdOracle.sol, contracts/libraries/LibTractor.sol |
| `libraries/LibFunction.sol` | 44 | — |
| `libraries/LibGauge.sol` | 375 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/storage/System.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/libraries/Silo/LibWhitelist.sol, contracts/libraries/LibRedundantMath32.sol, contracts/libraries/Well/LibWell.sol, contracts/beanstalk/sun/GaugePointFacet.sol |
| `libraries/LibIncentive.sol` | 543 | ⚠️ @openzeppelin/contracts/utils/math/Math.sol, contracts/libraries/LibRedundantMath256.sol |
| `libraries/LibLockedUnderlying.sol` | 515 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/libraries/LibRedundantMath256.sol |
| `libraries/LibMarket.sol` | 28 | — |
| `libraries/LibPRBMathRoundable.sol` | 33 | ⚠️ @prb/math/contracts/PRBMath.sol |
| `libraries/LibReceiving.sol` | 153 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/C.sol, contracts/libraries/LibAppStorage.sol, contracts/beanstalk/storage/System.sol, contracts/libraries/LibFertilizer.sol |
| `libraries/LibRedundantMath128.sol` | 90 | — |
| `libraries/LibRedundantMath256.sol` | 90 | — |
| `libraries/LibRedundantMath32.sol` | 90 | — |
| `libraries/LibRedundantMathSigned128.sol` | 90 | — |
| `libraries/LibRedundantMathSigned256.sol` | 90 | — |
| `libraries/LibRedundantMathSigned96.sol` | 90 | — |
| `libraries/LibShipping.sol` | 121 | ⚠️ contracts/libraries/LibAppStorage.sol, contracts/libraries/LibReceiving.sol, contracts/beanstalk/storage/System.sol, contracts/ecosystem/ShipmentPlanner.sol |
| `libraries/LibTractor.sol` | 185 | ⚠️ contracts/C.sol |
| `libraries/LibUnripe.sol` | 260 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/libraries/LibRedundantMath256.sol, contracts/interfaces/basin/IWell.sol, contracts/interfaces/basin/IWellFunction.sol |
| `libraries/Minting/LibMinting.sol` | 24 | ⚠️ contracts/libraries/LibRedundantMath256.sol, contracts/C.sol |
| `libraries/Minting/LibWellMinting.sol` | 187 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/interfaces/basin/pumps/ICumulativePump.sol, contracts/interfaces/basin/pumps/ICappedReservesPump.sol, contracts/interfaces/basin/pumps/IInstantaneousPump.sol, contracts/interfaces/basin/IWell.sol, contracts/libraries/Well/LibWell.sol, contracts/libraries/LibRedundantMathSigned256.sol, contracts/libraries/Oracle/LibEthUsdOracle.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/libraries/LibRedundantMath256.sol, contracts/interfaces/basin/IBeanstalkWellFunction.sol |
| `libraries/Oracle/LibChainlinkOracle.sol` | 197 | ⚠️ contracts/C.sol, contracts/interfaces/chainlink/IChainlinkAggregator.sol, contracts/libraries/LibRedundantMath256.sol |
| `libraries/Oracle/LibDeltaB.sol` | 178 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/C.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibRedundantMathSigned256.sol, contracts/interfaces/basin/IWell.sol, contracts/interfaces/basin/pumps/ICappedReservesPump.sol, contracts/interfaces/basin/IBeanstalkWellFunction.sol |
| `libraries/Oracle/LibEthUsdOracle.sol` | 66 | ⚠️ contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibAppStorage.sol, contracts/C.sol, contracts/libraries/Oracle/LibOracleHelpers.sol |
| `libraries/Oracle/LibOracleHelpers.sol` | 29 | ⚠️ contracts/libraries/LibRedundantMath256.sol |
| `libraries/Oracle/LibUniswapOracle.sol` | 70 | ⚠️ @uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol, @openzeppelin/contracts/utils/math/SafeCast.sol, @uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol, contracts/C.sol |
| `libraries/Oracle/LibUsdOracle.sol` | 176 | ⚠️ @uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol, @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol, contracts/C.sol, contracts/libraries/LibAppStorage.sol, contracts/beanstalk/storage/System.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/libraries/LibRedundantMath256.sol, forge-std/console.sol |
| `libraries/Oracle/LibWstethEthOracle.sol` | 99 | ⚠️ contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibAppStorage.sol, contracts/C.sol, contracts/libraries/Oracle/LibOracleHelpers.sol |
| `libraries/Oracle/LibWstethUsdOracle.sol` | 48 | ⚠️ contracts/libraries/Oracle/LibWstethEthOracle.sol, contracts/libraries/Oracle/LibEthUsdOracle.sol |
| `libraries/Silo/LibFlood.sol` | 382 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/C.sol, contracts/interfaces/basin/IWell.sol, contracts/libraries/Well/LibWell.sol, contracts/beanstalk/storage/Account.sol, contracts/libraries/Oracle/LibDeltaB.sol, contracts/libraries/LibRedundantMath256.sol, contracts/libraries/LibAppStorage.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol |
| `libraries/Silo/LibGerminate.sol` | 538 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/storage/System.sol, contracts/libraries/LibRedundantMath256.sol |
| `libraries/Silo/LibLegacyWhitelist.sol` | 56 | ⚠️ contracts/libraries/Silo/LibTokenSilo.sol |
| `libraries/Silo/LibSilo.sol` | 727 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/storage/System.sol, contracts/libraries/LibRedundantMath256.sol, contracts/interfaces/basin/IWell.sol, contracts/libraries/Silo/LibFlood.sol |
| `libraries/Silo/LibSiloPermit.sol` | 222 | ⚠️ @openzeppelin/contracts/utils/cryptography/ECDSA.sol |
| `libraries/Silo/LibTokenSilo.sol` | 620 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/libraries/LibRedundantMath256.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/storage/System.sol, contracts/libraries/LibRedundantMath32.sol, contracts/libraries/LibRedundantMath128.sol, contracts/libraries/LibRedundantMathSigned128.sol, contracts/libraries/LibRedundantMathSigned96.sol, contracts/libraries/LibBytes.sol, contracts/libraries/Silo/LibGerminate.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/libraries/LibTractor.sol |
| `libraries/Silo/LibWhitelist.sol` | 554 | ⚠️ @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/beanstalk/storage/System.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/libraries/Silo/LibTokenSilo.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/libraries/LibUnripe.sol, contracts/libraries/Well/LibWell.sol, contracts/interfaces/chainlink/IChainlinkAggregator.sol, contracts/libraries/LibRedundantMath32.sol |
| `libraries/Silo/LibWhitelistedTokens.sol` | 330 | ⚠️ contracts/libraries/LibAppStorage.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/storage/System.sol, contracts/libraries/Well/LibWell.sol |
| `libraries/Token/LibApprove.sol` | 21 | ⚠️ @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol |
| `libraries/Token/LibBalance.sol` | 108 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol, @openzeppelin/contracts/utils/math/Math.sol, @openzeppelin/contracts/utils/math/SafeCast.sol, contracts/libraries/LibRedundantMath256.sol, contracts/beanstalk/storage/AppStorage.sol |
| `libraries/Token/LibEth.sol` | 22 | — |
| `libraries/Token/LibTokenApprove.sol` | 43 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/beanstalk/storage/AppStorage.sol |
| `libraries/Token/LibTokenPermit.sol` | 103 | ⚠️ @openzeppelin/contracts/utils/cryptography/ECDSA.sol |
| `libraries/Token/LibTransfer.sol` | 100 | ⚠️ @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol |
| `libraries/Token/LibWeth.sol` | 37 | — |
| `libraries/Well/LibWell.sol` | 320 | ⚠️ @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/libraries/LibRedundantMath256.sol, contracts/interfaces/basin/pumps/ICumulativePump.sol, contracts/interfaces/basin/IWell.sol, contracts/C.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/libraries/Oracle/LibUsdOracle.sol, contracts/libraries/LibRedundantMath128.sol |
| `libraries/Well/LibWellBdv.sol` | 53 | ⚠️ contracts/libraries/LibRedundantMath256.sol, contracts/interfaces/basin/pumps/IInstantaneousPump.sol, contracts/interfaces/basin/IWell.sol, contracts/interfaces/basin/IWellFunction.sol, contracts/libraries/Well/LibWell.sol, contracts/C.sol |
| `mocks/MockChecker.sol` | 26 | — |
| `mocks/MockContract.sol` | 21 | — |
| `mocks/MockDiamond.sol` | 54 | ⚠️ @openzeppelin/contracts/utils/introspection/IERC165.sol |
| `mocks/MockERC1155.sol` | 12 | ⚠️ @openzeppelin/contracts/token/ERC1155/ERC1155.sol |
| `mocks/MockERC721.sol` | 17 | ⚠️ @openzeppelin/contracts/token/ERC721/ERC721.sol |
| `mocks/MockFertilizer.sol` | 17 | ⚠️ contracts/tokens/Fertilizer/Fertilizer.sol |
| `mocks/MockGaugePoint.sol` | 49 | — |
| `mocks/MockInitDiamond.sol` | 70 | ⚠️ contracts/beanstalk/init/InitWhitelist.sol, contracts/beanstalk/init/InitWhitelistStatuses.sol, contracts/libraries/LibGauge.sol, contracts/libraries/LibTractor.sol, contracts/beanstalk/sun/SeasonFacet/Weather.sol |
| `mocks/MockLiquidityWeight.sol` | 41 | — |
| `mocks/MockMetadataERC1155.sol` | 45 | ⚠️ @openzeppelin/contracts/token/ERC1155/ERC1155.sol |
| `mocks/MockOracle.sol` | 50 | — |
| `mocks/MockToken.sol` | 57 | ⚠️ @openzeppelin/contracts/token/ERC20/ERC20.sol, @openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol, @openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol |
| `mocks/MockUpgradeInitDiamond.sol` | 16 | — |
| `mocks/MockWETH.sol` | 33 | — |
| `mocks/MockWsteth.sol` | 28 | ⚠️ contracts/libraries/Oracle/LibWstethEthOracle.sol |
| `mocks/TestnetMetadataFacet.sol` | 104 | ⚠️ contracts/beanstalk/metadata/MetadataImage.sol, @openzeppelin/contracts/utils/Strings.sol, contracts/libraries/LibBytes.sol, contracts/libraries/Silo/LibTokenSilo.sol, contracts/libraries/LibRedundantMath256.sol |
| `mocks/chainlink/MockChainlinkAggregator.sol` | 108 | ⚠️ contracts/interfaces/chainlink/IChainlinkAggregator.sol |
| `mocks/chainlink/MockChainlinkPriceFeedRegistry.sol` | 25 | ⚠️ contracts/C.sol |
| `mocks/mockFacets/MockAdminFacet.sol` | 83 | ⚠️ contracts/C.sol, contracts/libraries/Token/LibTransfer.sol, contracts/beanstalk/sun/SeasonFacet/SeasonFacet.sol, contracts/beanstalk/sun/SeasonFacet/Sun.sol, contracts/libraries/Token/LibBalance.sol, contracts/beanstalk/storage/System.sol, contracts/libraries/LibShipping.sol, contracts/libraries/LibReceiving.sol |
| `mocks/mockFacets/MockConvertFacet.sol` | 58 | ⚠️ @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol |
| `mocks/mockFacets/MockExploitFacet.sol` | 105 | ⚠️ contracts/C.sol, contracts/libraries/Token/LibTransfer.sol, contracts/beanstalk/Invariable.sol |
| `mocks/mockFacets/MockFertilizerFacet.sol` | 50 | ⚠️ contracts/beanstalk/barn/FertilizerFacet.sol |
| `mocks/mockFacets/MockFieldFacet.sol` | 218 | ⚠️ contracts/libraries/LibRedundantMath256.sol, contracts/beanstalk/field/FieldFacet.sol, @openzeppelin/contracts/utils/math/Math.sol, contracts/libraries/LibPRBMathRoundable.sol |
| `mocks/mockFacets/MockSeasonFacet.sol` | 744 | ⚠️ contracts/libraries/LibRedundantMath256.sol, contracts/beanstalk/sun/SeasonFacet/SeasonFacet.sol, contracts/libraries/LibBytes.sol, @openzeppelin/contracts/token/ERC1155/IERC1155.sol, contracts/beanstalk/storage/System.sol, contracts/libraries/LibDiamond.sol, contracts/libraries/Oracle/LibChainlinkOracle.sol, contracts/libraries/Oracle/LibEthUsdOracle.sol, contracts/libraries/Oracle/LibWstethEthOracle.sol, contracts/libraries/Oracle/LibWstethUsdOracle.sol, contracts/libraries/Oracle/LibUsdOracle.sol, contracts/libraries/LibAppStorage.sol, contracts/libraries/LibRedundantMathSigned256.sol, contracts/libraries/LibGauge.sol, contracts/libraries/LibRedundantMath32.sol, contracts/libraries/Minting/LibWellMinting.sol, contracts/libraries/LibEvaluate.sol, contracts/libraries/Silo/LibTokenSilo.sol, contracts/interfaces/basin/IWell.sol, contracts/libraries/LibReceiving.sol, contracts/libraries/Silo/LibFlood.sol |
| `mocks/mockFacets/MockSiloFacet.sol` | 351 | ⚠️ contracts/libraries/LibRedundantMath256.sol |
| `mocks/mockFacets/MockUnripeFacet.sol` | 42 | ⚠️ contracts/beanstalk/barn/UnripeFacet.sol, contracts/libraries/LibAppStorage.sol, contracts/libraries/LibTractor.sol |
| `mocks/mockFacets/MockUpgradeFacet.sol` | 15 | — |
| `mocks/mockFacets/MockWhitelistFacet.sol` | 133 | ⚠️ contracts/beanstalk/silo/WhitelistFacet/WhitelistFacet.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol |
| `mocks/newMockInitDiamond.sol` | 217 | ⚠️ contracts/beanstalk/init/InitalizeDiamond.sol, contracts/beanstalk/storage/AppStorage.sol, contracts/beanstalk/storage/System.sol, contracts/libraries/Silo/LibWhitelistedTokens.sol, contracts/libraries/Silo/LibWhitelist.sol, contracts/libraries/LibUnripe.sol, contracts/beanstalk/silo/BDVFacet.sol, contracts/C.sol |
| `mocks/uniswap/MockUniswapV3Deployer.sol` | 44 | ⚠️ @uniswap/v3-core/contracts/interfaces/IUniswapV3PoolDeployer.sol |
| `mocks/uniswap/MockUniswapV3Factory.sol` | 58 | — |
| `mocks/uniswap/MockUniswapV3Pool.sol` | 107 | ⚠️ @uniswap/v3-core/contracts/libraries/Tick.sol, @uniswap/v3-core/contracts/libraries/Oracle.sol, @uniswap/v3-core/contracts/libraries/TickMath.sol, @uniswap/v3-core/contracts/interfaces/IUniswapV3PoolDeployer.sol |
| `mocks/well/MockPump.sol` | 89 | ⚠️ contracts/interfaces/basin/pumps/IInstantaneousPump.sol, contracts/interfaces/basin/pumps/ICumulativePump.sol |
| `mocks/well/MockSetComponentsWell.sol` | 304 | ⚠️ @openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol, contracts/interfaces/basin/IWell.sol, contracts/interfaces/basin/pumps/IPump.sol, contracts/interfaces/basin/IWellFunction.sol |
| `pipeline/Pipeline.sol` | 119 | ⚠️ @openzeppelin/contracts/token/ERC1155/utils/ERC1155Holder.sol, @openzeppelin/contracts/token/ERC721/utils/ERC721Holder.sol |
| `pipeline/junctions/UnwrapAndSendETH.sol` | 33 | — |
| `tokens/Bean.sol` | 15 | — |
| `tokens/ERC20/BeanstalkERC20.sol` | 67 | ⚠️ @openzeppelin/contracts/access/AccessControl.sol, @openzeppelin/contracts/utils/Context.sol, @openzeppelin/contracts/token/ERC20/ERC20.sol, @openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol, @openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol |
| `tokens/Fertilizer/Fertilizer.sol` | 126 | ⚠️ contracts/libraries/LibRedundantMath128.sol, contracts/libraries/LibRedundantMath256.sol |
| `tokens/Fertilizer/Fertilizer1155.sol` | 157 | ⚠️ @openzeppelin/contracts-upgradeable/token/ERC1155/ERC1155Upgradeable.sol, @openzeppelin/contracts/token/ERC1155/IERC1155Receiver.sol, contracts/libraries/LibFertilizer.sol |
| `tokens/Fertilizer/Internalizer.sol` | 86 | ⚠️ @openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol, @openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol, @openzeppelin/contracts/token/ERC20/IERC20.sol, contracts/libraries/LibRedundantMath32.sol, contracts/libraries/LibRedundantMath128.sol, @openzeppelin/contracts/utils/Strings.sol |
| `tokens/UnripeBean.sol` | 15 | — |
| `tokens/UnripeBean3Crv.sol` | 15 | — |

**Total LOC: 30,805**

> ⚠️ = imports that resolve outside the scope directory (external dependency)