# Context Pack
Generated: 2026-05-29T20:25:38.212883+00:00
Audit: beanstalk-2024-05-eval2  |  Target: Beanstalk The Finale (API-free eval2)

> Navigation index — table format only. Every line is a file:line pointer; agents fetch depth on demand.

---

## Scope Summary

**Protocol:** Beanstalk The Finale (API-free eval2)  **Language:** Solidity

**Entry points (455):**
  - `LibGauge.stepGauge`
  - `LibLockedUnderlying.getLockedUnderlying`
  - `LibIncentive.determineReward`
  - `LibShipping.ship`
  - `LibShipping.getBeansFromPoints`
  - `LibShipping.getShipmentPlans`
  - `ShipmentPlanner.isFertilizing`
  - `ShipmentPlanner.getBarnPlan`
  - `ShipmentPlanner.getFieldPlan`
  - `ShipmentPlanner.getSiloPlan`
  - `Drafter.encodeOperatorPasteInstr`
  - `Drafter.decodeOperatorPasteInstr`
  - `Drafter.encodeLibReturnPasteParam`
  - `Drafter.decodeLibReturnPasteParam`
  - `Drafter.encodeClipboard`
  - … and 440 more

**Detected:** ERC-4626 vault, proxy/upgradeable

---

## Priority Investigation Clusters

> Ranked by externally-reachable tainted **sinks**, then static-analysis severity. Start here — the Sinks column is the strongest signal for attacker reachability. Clusters with no High/Med/sink signal are lower priority unless your specialty has a specific reason to inspect them.

| Cluster (dir) | High | Med | Sinks | Representative files |
|---|---|---|---|---|
| `contracts/beanstalk/init/reseed/L2` | 1 | 9 | 16 | ReseedBarn.sol, ReseedBean.sol, ReseedInternalBalances.sol, ReseedSilo.sol, +1 |
| `contracts/tokens/Fertilizer` | 1 | 2 | 12 | Fertilizer.sol, Fertilizer1155.sol, Internalizer.sol |
| `contracts/beanstalk/market/MarketplaceFacet` | 0 | 2 | 11 | Listing.sol, MarketplaceFacet.sol, Order.sol, PodTransfer.sol |
| `contracts/beanstalk/migration/L1Libraries` | 4 | 1 | 8 | LibEth.sol, LibL1AppStorage.sol, LibTransfer.sol, LibWeth.sol |
| `contracts/beanstalk/sun/SeasonFacet` | 1 | 11 | 5 | SeasonFacet.sol, SeasonGettersFacet.sol, Sun.sol, Weather.sol |
| `contracts/beanstalk/barn` | 1 | 1 | 5 | FertilizerFacet.sol, UnripeFacet.sol |
| `contracts/beanstalk/silo/SiloFacet` | 0 | 12 | 4 | ClaimFacet.sol, SiloFacet.sol, SiloGettersFacet.sol, TokenSilo.sol |
| `contracts/pipeline` | 1 | 0 | 2 | Pipeline.sol |

**Lower priority — no High/Med/sink signal:** `contracts/interfaces`, `contracts/ecosystem/price`, `contracts/beanstalk/field`, `contracts/beanstalk/sun`, `contracts/interfaces/basin`

---

## Top 20 Static Findings

| Severity | Confidence | File | Description |
|---|---|---|---|
| High | High | contracts/beanstalk/migration/L1Libraries/LibTransfer.sol | LibTransfer.transferToken(IERC20,address,address,uint256,LibTransfer.From,LibTra |
| High | High | contracts/beanstalk/barn/UnripeFacet.sol | UnripeFacet.addMigratedUnderlying(address,uint256) (contracts/beanstalk/barn/Unr |
| High | High | contracts/beanstalk/init/reseed/L2/ReseedBean.sol | ReseedBean.mintAndSync(BeanstalkERC20,address,uint256,uint256) (contracts/beanst |
| High | High | contracts/beanstalk/migration/L1Libraries/LibTransfer.sol | LibTransfer.receiveToken(IERC20,uint256,address,LibTransfer.From) (contracts/bea |
| High | High | contracts/tokens/Fertilizer/Internalizer.sol | Internalizer.uri(uint256) (contracts/tokens/Fertilizer/Internalizer.sol#35-37) c |
| High | High | contracts/beanstalk/metadata/MetadataFacet.sol | MetadataFacet.uri(uint256) (contracts/beanstalk/metadata/MetadataFacet.sol#33-83 |
| High | High | contracts/beanstalk/metadata/MetadataImage.sol | MetadataImage.s (contracts/beanstalk/metadata/MetadataImage.sol#20) is never ini |
| High | High | contracts/beanstalk/sun/SeasonFacet/SeasonGettersFacet.sol | SeasonGettersFacet.s (contracts/beanstalk/sun/SeasonFacet/SeasonGettersFacet.sol |
| High | Medium | contracts/beanstalk/migration/L1Libraries/LibEth.sol | LibEth.refundEth() (contracts/beanstalk/migration/L1Libraries/LibEth.sol#16-22)  |
| High | Medium | contracts/pipeline/Pipeline.sol | Pipeline._pipeMem(address,bytes,uint256) (contracts/pipeline/Pipeline.sol#82-91) |
| High | Medium | contracts/beanstalk/migration/L1Libraries/LibWeth.sol | LibWeth.unwrap(uint256,LibTransfer.From) (contracts/beanstalk/migration/L1Librar |
| High | Medium | contracts/pipeline/junctions/UnwrapAndSendETH.sol | UnwrapAndSendETH.unwrapAndSendETH(address) (contracts/pipeline/junctions/UnwrapA |
| High | Medium | contracts/beanstalk/init/reseed/L1/ReseedL2Migration.sol | ReseedL2Migration.init() (contracts/beanstalk/init/reseed/L1/ReseedL2Migration.s |
| High | Medium | contracts/beanstalk/init/reseed/L1/ReseedL2Migration.sol | ReseedL2Migration.init() (contracts/beanstalk/init/reseed/L1/ReseedL2Migration.s |
| High | Medium | contracts/beanstalk/init/reseed/L1/ReseedL2Migration.sol | ReseedL2Migration.init() (contracts/beanstalk/init/reseed/L1/ReseedL2Migration.s |
| Medium | High | contracts/beanstalk/migration/L1Libraries/LibTransfer.sol | LibTransfer.sendToken(IERC20,uint256,address,LibTransfer.To) (contracts/beanstal |
| Medium | High | contracts/beanstalk/Invariable.sol | Invariable.noNetFlow() (contracts/beanstalk/Invariable.sol#52-69) uses a dangero |
| Medium | High | contracts/beanstalk/silo/ApprovalFacet.sol | Contract locking ether found: 	Contract ApprovalFacet (contracts/beanstalk/silo/ |
| Medium | High | contracts/beanstalk/silo/L2ContractMigrationFacet.sol | Contract locking ether found: 	Contract L2ContractMigrationFacet (contracts/bean |
| Medium | High | contracts/beanstalk/silo/EnrootFacet.sol | Contract locking ether found: 	Contract EnrootFacet (contracts/beanstalk/silo/En |

---

## KB + Immunefi Crossref Gaps

| Pattern | Source | File(s) | Defense Status | Notes |
|---|---|---|---|---|
| ERC-4626 | Immunefi | — | Unknown | 57335 sc medium zero min out erc 4626 deposits cause under m |
| ERC-4626 | Immunefi | — | Unknown | 56907 sc critical attacker can steal first depositor s asset |
| ERC-4626 | Immunefi | — | Unknown | 56941 sc critical staking vault vulnerable to first deposito |
| Governance | Immunefi | — | Unknown | 56798 sc critical flash vote exploit drains all funds via al |
| Governance | Immunefi | — | Unknown | 31507 - [SC - Critical] Malicious user could flash-loan the  |
| Governance | Immunefi | — | Unknown | 31552 - [SC - Insight] Lack of the validation for a Flash to |

---

## External Dependencies

  *(none detected)*

---

## Compiler Warnings

*(none)*

---

## Non-Issues (skip list — agents must NOT re-analyze)

  *(no fully-guarded paths identified)*
