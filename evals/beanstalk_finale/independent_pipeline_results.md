# Independent Pipeline Results — Beanstalk Finale (API-free eval2)

_BLIND run: produced before reading the public answer key. Frozen 2026-05-29T21:04Z._
_Pipeline: analyze → /deep-analysis → analyze-resume → /ite-audit (16 specialists) → full → /triage → review-gate. **Zero Anthropic API calls** (api_free pinned, key disabled)._

**Totals:** 48 merged findings → submit 16, poc_required 7, merged/dup 15, rejected 9, human-queue 7.

## Canonical findings — poc_required (High/Critical needing state-flip PoC)

### CC-001 — L1->L2 migration redemption has no spent-marker and uses += accounting, allowing unbounded replay of a single proof/signature to mint unbacked deposits, stalk and roots
- **Severity:** Critical  ·  **Status:** poc_required  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/silo/L2ContractMigrationFacet.sol :: redeemDepositsAndInternalBalances
- **Impact:** An attacker observes any legitimate migration redemption (or front-runs one), then replays the identical calldata repeatedly. stalk and roots are inflated without backing on each replay; stalk and roots are the governance vote weight and the divisor/numerator for earned-Bean (mint) distribution. Unb
- **Decision:** Confirmed in source: redeemDepositsAndInternalBalances (L88-114) verifies a static Merkle proof + EIP-712 sig but writes NO spent/nonce marker; setStalk (L206-207) uses += for stalk and roots. Proof+signature are public calldata, so the identical call is replayable until deadline, each replay re-add

### CC-003 — Migration Merkle leaf omits reciever, so any holder of the public L1 signature can redirect another contract's migration credit to an attacker-chosen L2 address
- **Severity:** High  ·  **Status:** poc_required  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/silo/L2ContractMigrationFacet.sol :: verifyDepositsAndInternalBalances
- **Impact:** The migration deposit/stalk/roots credit for an L1 contract can be redirected to and/or duplicated at an attacker-chosen L2 address using the publicly visible signature, rather than only the originally intended reciever. Standalone this is an authorization-binding gap; combined with CC-001 it conver
- **Decision:** Confirmed: verifyDepositsAndInternalBalances leaf = keccak256(account, deposits, internalBalances, ownerRoots) (L127) omits reciever; destination is bound only by the EIP-712 signature (L144), which is public calldata. The immutable MERKLE_ROOT never constrains the L2 destination. Standalone a weak 

### LG-001 — L2ContractMigrationFacet zeroes global per-token silo balances on every redeem
- **Severity:** High  ·  **Status:** poc_required  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/silo/L2ContractMigrationFacet.sol :: addMigratedDepositsToAccount
- **Impact:** Global deposited/depositedBdv for every token routed through contract migration is set to 0 while per-account deposits exist, breaking the core invariant total == sum(accounts) (ACC-002). Downstream consumers that read s.sys.silo.balances[token] for BDV ratios, convert valuation, gauge weighting and
- **Decision:** Confirmed in source: addMigratedDepositsToAccount declares uint128 totalDeposited/totalDepositedBdv (L159-160), never increments them, then writes them to s.sys.silo.balances[token].deposited/.depositedBdv (L194-195) -- always 0 -- on every permissionless redeem. Hard assignment clobbers any prior R

### PC-001 — L1->L2 reseed never initializes global Silo total stalk/roots (s.sys.silo.stalk / s.sys.silo.roots), breaking the protocol-wide stalk-conservation invariant and corrupting roots/earned-Bean accounting for the entire migrated population
- **Severity:** High  ·  **Status:** poc_required  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/init/reseed/L2/ReseedSilo.sol :: reseedSiloDeposit / init
- **Impact:** Permanent post-migration corruption of the global Silo stalk/roots accounting for the whole protocol: reseeded depositors hold stalk with zero roots and therefore earn near-zero share of all future earned-Bean (sunrise) distributions, while the first post-migration actor mints genesis-scale roots an
- **Decision:** Confirmed by grep over beanstalk/init/: NO write to s.sys.silo.stalk or s.sys.silo.roots anywhere in the reseed/init tree (only per-account s.accts[].stalk in ReseedSilo L164). After the L2 reseed, accounts hold stalk but globals are 0. Consumers: burnActiveStalk/transferStalk divide by s.sys.silo.s

### EA-001 — Flood (Season of Plenty) mints and dumps Beans sized by instantaneous well reserves and swaps with zero slippage, enabling flash-loan over-mint + sandwich of stalkholder proceeds
- **Severity:** High  ·  **Status:** poc_required  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/libraries/Silo/LibFlood.sol :: sopWell / getWellsByDeltaB / calculateSopPerWell
- **Impact:** Stalkholders receive materially less SOP plenty than the Flood mints; the shortfall is captured by the MEV/sandwich actor. Combined with instantaneous-reserve sizing, an attacker can also force a larger Bean mint+dump than the protocol intends, deepening the post-flood depeg. Value-at-risk per flood
- **Decision:** Confirmed structure: LibFlood handleRain (flood branch) sizes SOP from getWellsByDeltaB -> currentDeltaB(well) -> getReserves (INSTANTANEOUS spot reserves, not the cumulative-pump TWAP the mint uses), then sopWell mints and swaps with minAmountOut=0 / deadline=max. Flood is permissionlessly triggera

### FL-001 — Convert stalk-penalty before/after deltaB uses uncapped spot reserves while the convert-capacity ceiling uses the capped pump, letting a flash-loan-skewed well under-report against-peg movement and avoid the stalk penalty
- **Severity:** Medium  ·  **Status:** poc_required  ·  **Confidence:** Medium
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/libraries/Convert/LibPipelineConvert.sol :: populatePipelineConvertData / prepareStalkPenaltyCalculation
- **Impact:** Stalk-penalty avoidance / convert-capacity-ceiling bypass: a convert that should incur a stalk penalty (or be rejected in the non-pipeline ConvertFacet.convert path) measures zero/under-stated against-peg movement on flash-loan-skewed spot reserves, so the user retains more grown stalk than the capp
- **Decision:** Confirmed structure: LibPipelineConvert measures before/after deltaB for the stalk penalty via uncapped instantaneous spot reserves (LibDeltaB.currentDeltaB -> getReserves, ZERO_LOOKBACK), while the convert-capacity ceiling uses the capped Multi-Flow pump. Since pipelineConvert runs attacker-supplie

### RE-001 — Arbitrary-call facets (Farm/Depot/Tractor) lack nonReentrant guard
- **Severity:** Medium  ·  **Status:** poc_required  ·  **Confidence:** Medium
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/farm/FarmFacet.sol :: farm / advancedFarm (also DepotFacet.advancedPipe, TractorFacet.tractor, LibPipelineConvert.executeAdvancedFarmCalls)
- **Impact:** An external call routed through Pipeline/Farm/Depot can re-enter the diamond and reach unguarded state-mutating functions (sow, harvest, sunrise, mintFertilizer) while an outer arbitrary-call batch is mid-execution and internal accounting (stalk/deltaB/season) is transiently inconsistent. Token cust
- **Decision:** Confirmed structure: FarmFacet.farm/advancedFarm, DepotFacet pipe family, TractorFacet.tractor and LibPipelineConvert.executeAdvancedFarmCalls carry NO nonReentrant; the shared diamond guard is only set by guarded callers, so entering through one of these arbitrary-call entrypoints leaves the flag u


## Canonical findings — submit

### CC-002 — BeanL1RecieverFacet caps migrated L1 Beans at EXTERNAL_L1_BEANS = 0, so every L2 mint reverts after the user's L1 Beans are already burned (permanent cross-chain fund loss)
- **Severity:** High  ·  **Status:** submit  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/migration/BeanL1RecieverFacet.sol :: recieveL1Beans
- **Impact:** Direct, permanent loss of all externally-held L1 Beans that attempt migration: L1 burn succeeds, the corresponding L2 mint always reverts because the migration cap is 0. No attacker is required; the migration path is fully bricked and every user who uses it loses funds. Critical under Immunefi v2.2 
- **Decision:** Confirmed in source: BeanL1RecieverFacet EXTERNAL_L1_BEANS=0 (L22); recieveL1Beans does migratedL1Beans += amount then require(EXTERNAL_L1_BEANS >= migratedL1Beans) (L40), i.e. require(0 >= positive), always false for amount>0, so C.bean().mint (L43) is unreachable. The companion L1 path burns Beans

### LG-002 — ReseedSilo overwrites account stalk per token (= not +=), zeroing multi-token depositors
- **Severity:** High  ·  **Status:** submit  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/init/reseed/L2/ReseedSilo.sol :: reseedSiloDeposit
- **Impact:** Every multi-token depositor loses all stalk except their last-token contribution after the L1->L2 reseed, permanently reducing or zeroing their governance weight and earned-Bean (yield) share. Stalk is consumed by LibSilo root issuance and LibReceiving earned-Bean distribution; the loss is permanent
- **Decision:** Confirmed in source: ReseedSilo.reseedSiloDeposit L164 `s.accts[deposits.accounts].stalk = accountStalk` is a plain assignment, and init() calls it once per token (bean, beanEth, beanWstEth, bean3Crv, urBean, urBeanLp) over the same account keys. Any multi-token holder is overwritten on each subsequ

### DT-004 — ReseedField inner loop increments wrong counter (i instead of j), bricking Field migration
- **Severity:** High  ·  **Status:** submit  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/init/reseed/L2/ReseedField.sol :: init
- **Impact:** ReseedField.init reverts for any input containing plots, so the migration upgrade cannot reseed the Field. Pods cannot be migrated to L2 — migration DoS / loss of field positions until patched.
- **Decision:** Confirmed in source: ReseedField.init inner loop header L49 `for (uint j; j < accountPlots[i].plots.length; i++)` increments outer i, not inner j. j never advances and i runs out of bounds -> revert (or non-terminating before OOB). Any reseed input containing plots reverts, so the one-shot Field mig

### BSA-001 — LibChainlinkOracle.getTokenPrice NatSpec states lookback>0 returns TWAP, but the ternary returns spot for lookback>0 and divides-by-zero for lookback==0
- **Severity:** Medium  ·  **Status:** submit  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/libraries/Oracle/LibChainlinkOracle.sol :: getTokenPrice
- **Impact:** Any internal consumer that follows the documented convention and passes lookback>0 expecting manipulation resistance instead consumes the instantaneous spot price. If a reachable mint/convert/peg path (LibEthUsdOracle -> LibWellMinting/LibDeltaB -> sunrise Bean issuance / convert valuation) requests
- **Decision:** Confirmed in source (LibChainlinkOracle.getTokenPrice L45-47): `lookback > 0 ? getPrice(...) : getTwap(..., lookback)` is inverted vs NatSpec (L34-37: lookback>0 = TWAP). A TWAP request returns spot; a spot request calls getTwap(...,0) which divides by lookback=0 (revert), also breaking the document

### DS-003 — LibUsdOracle 1e24/price no zero-check: frozen feed reverts, DoSing sunrise
- **Severity:** Medium  ·  **Status:** submit  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/libraries/Oracle/LibUsdOracle.sol :: getTokenPriceFromExternal
- **Impact:** When a Chainlink feed backing a whitelisted token (encodeType 0x01) is frozen, stale beyond FOUR_HOUR_TIMEOUT, or reverting, every consumer of getUsdPrice/getTokenPriceFromExternal for that token reverts instead of receiving the documented 0 sentinel. Consumers include the sunrise oracle step and co
- **Decision:** Confirmed: getTokenPriceFromExternal encodeType 0x01 returns 1e24.div(LibChainlinkOracle.getTokenPrice(...)) (L120-127) with NO zero-guard, while the WETH/WSTETH branches guard price==0. LibChainlinkOracle returns 0 (not revert) on a broken/frozen feed, so 1e24/0 reverts instead of degrading to the 

### DT-011 — ReseedInternalBalances lacks farmers/balances length-equality check
- **Severity:** Low  ·  **Status:** submit  ·  **Confidence:** Medium
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/init/reseed/L2/ReseedInternalBalances.sol :: setInternalBalances
- **Impact:** Migration of internal balances reverts on malformed input (DoS of that reseed step). Bounded; the totalInternalBalance guard also catches mismatches. Medium.
- **Decision:** Confirmed: ReseedInternalBalances.setInternalBalances iterates i over farmers.length and reads balances[i] with no farmers.length==balances.length precondition; a short balances array reverts OOB, aborting the internal-balance reseed step (a longer one is caught by the totalInternalBalance guard). P

### BSA-005 — ReseedBarn struct @dev 'fertilizerIds MUST be in acsending order' is never enforced in mintFertilizers, allowing a malformed nextFid linked list
- **Severity:** Medium  ·  **Status:** submit  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/init/reseed/L2/ReseedBarn.sol :: mintFertilizers
- **Impact:** A non-ascending or duplicate-id input yields a malformed/cyclic fertilizer linked list. Sun fertilizer payout traverses nextFid in id order to pay Beans to fertilizer holders; a corrupted chain strands or mispays fertilizer (holders past the break never get paid, or a cycle disrupts iteration). Boun
- **Decision:** Confirmed: ReseedBarn.mintFertilizers builds the nextFid linked list (fertFirst, nextFid[prev]=cur, fertLast) assuming ascending fertilizerIds, a 'MUST' stated only in NatSpec and never enforced. Out-of-order/duplicate input produces a malformed/cyclic list that strands or mispays Sun fertilizer pay

### AR-001 — getAverageGrownStalkPerBdv underflows when total stalk-per-BDV falls below STALK_BDV_PRECISION, reverting stepGauge and bricking season advancement
- **Severity:** Medium  ·  **Status:** submit  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/libraries/LibGauge.sol :: getAverageGrownStalkPerBdv
- **Impact:** Checked-subtraction underflow reverts the seed-gauge update, which runs inside sunrise/gm. Season advancement DoS (temporary protocol freeze) whenever the global stalk/BDV ratio is pushed below 1e4. Immunefi v2.2: temporary freezing of season progression / core protocol function -> High when chained
- **Decision:** Confirmed: LibGauge.getAverageGrownStalkPerBdv computes stalk.div(totalBdv).sub(STALK_BDV_PRECISION) with checked .sub and no floor; if stalk/totalBdv < 1e4 the subtraction reverts, and getAverageGrownStalkPerBdv -> stepGauge runs inside sunrise/gm, so every season advance reverts. The depressed-rat

### EA-002 — floodPodline mints 0.1% of Bean supply to the Field every Flood season, harvestable in pod (FIFO) order — front-runnable by buying the front of the pod line before an Oversaturation streak
- **Severity:** Medium  ·  **Status:** submit  ·  **Confidence:** Medium
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/libraries/Silo/LibFlood.sol :: floodPodline
- **Impact:** An actor timing the controllable Flood schedule can convert held Beans into a near-deterministic stream of Field harvest at the front of the pod line, advantaging informed/MEV-capable participants over passive Pod holders. Bounded to 0.1% of supply per flood season and to the front of the line; no p
- **Decision:** Confirmed: LibFlood.floodPodline makes ~0.1% of Bean supply of Pods harvestable each flood season, consumed FIFO. Flood is permissionlessly triggerable via sunrise after Oversaturation, so an actor who accumulates front-of-line Pods can convert a controllable flood schedule into a near-deterministic

### DS-004 — LibFlood.calculateSopPerWell div-by-(i-1)=0 reverts flood path in sunrise
- **Severity:** Medium  ·  **Status:** submit  ·  **Confidence:** Medium
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/libraries/Silo/LibFlood.sol :: calculateSopPerWell
- **Impact:** In a multi-well configuration with mixed-sign deltaBs during a Season of Plenty, the per-well sop allocation can divide by zero and revert. Because the flood logic runs inside the sunrise (gm) call, that revert blocks season advancement for the affected season until the deltaB distribution changes (
- **Decision:** Confirmed: LibFlood.calculateSopPerWell final loop `for (i = positiveDeltaBCount; i > 0; i--)` executes `shaveToLevel += (shaveToLevel - uint(wellDeltaBs[i-1].deltaB)) / (i - 1)` inside the shave branch; on the last iteration i==1 so (i-1)==0 -> division-by-zero panic, reverting. calculateSopPerWell

### CC-005 — Migration EIP-712 domain separator hardcodes L1 chainId and lacks any per-message nonce or destination-L2 binding, enabling cross-deployment/multi-L2 signature reuse
- **Severity:** Medium  ·  **Status:** submit  ·  **Confidence:** Medium
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/silo/L2ContractMigrationFacet.sol :: _domainSeparatorV4
- **Impact:** Cross-deployment / multi-L2 replay of a single migration signature and absence of a nonce that would otherwise bound CC-001. On a single-L2 deployment the practical impact is subsumed by CC-001; the standalone severity (signature not scoped to destination chain + no nonce) is Medium. The hardcoded l
- **Decision:** Confirmed: the migration EIP-712 domain uses C.getLegacyChainId() (hardcoded 1) and address(this), and the struct hash covers only (owner, reciever, deadline) -- no nonce and no destination-L2 binding. A single owner signature is valid on any L2 deployment sharing the diamond address and the hardcod

### OR-002 — LibUsdOracle.getTokenPrice WSTETH branch drops lookback, always returns spot wstETH/USD
- **Severity:** Medium  ·  **Status:** submit  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/libraries/Oracle/LibUsdOracle.sol :: getTokenPrice
- **Impact:** TWAP requests for wstETH via getTokenPrice silently return spot, removing the intended smoothing. The Uniswap V3 wstETH:ETH leg inside LibWstethEthOracle is AMM-based, so forcing its short FIFTEEN_MINUTES window (spot path) rather than the requested longer lookback weakens manipulation resistance fo
- **Decision:** Confirmed: LibUsdOracle.getTokenPrice WETH branch forwards lookback but the WSTETH branch hardcodes getWstethUsdPrice(0), dropping the caller's lookback so a TWAP request returns spot wstETH/USD. Sibling getUsdPrice forwards lookback for WSTETH, confirming this is an oversight. Weakens manipulation 

### OR-004 — LibWstethEthOracle returns 0 when Chainlink and Uniswap diverge >1% (no documented fallback)
- **Severity:** Medium  ·  **Status:** submit  ·  **Confidence:** Medium
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/libraries/Oracle/LibWstethEthOracle.sol :: getWstethEthPrice
- **Impact:** Any time the Chainlink wstETH:ETH feed and the Uniswap wstETH:ETH TWAP diverge by >=1% (plausible during volatility, a stETH depeg, or sustained Uniswap manipulation pressure), the wstETH oracle returns 0. For the BEAN:WSTETH well this turns the minting/deltaB oracle off (deltaB=0 in sunrise) or rev
- **Decision:** Confirmed: LibWstethEthOracle.getWstethEthPrice only assigns the price inside `if (getPercentDifference(chainlink, uniswap) < MAX_DIFFERENCE)` (1%) with no else/fallback, so on >=1% divergence it returns 0. A 0 propagates as oracle-failure (getUsdPrice 0 -> minting oracle off / LibDeltaB revert), pa

### OR-005 — Chainlink oracle ignores answeredInRound and has no min/max price bounds
- **Severity:** Low  ·  **Status:** submit  ·  **Confidence:** Medium
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/libraries/Oracle/LibChainlinkOracle.sol :: getPrice
- **Impact:** Stale (carried) Chainlink rounds within the 4h timeout and out-of-band circuit-breaker prices are accepted without rejection, feeding slightly-wrong USD prices into pricing/ratio math. Lower severity because Chainlink is the trusted source, the 0-on-failure design already handles outright outages, a
- **Decision:** Confirmed: LibChainlinkOracle validates only roundId!=0 + timestamp/answer freshness; it never checks answeredInRound>=roundId and applies no min/max sanity bounds, and uses a 4h timeout on feeds documented as 1h heartbeat. Carried-over stale rounds within 4h and circuit-breaker pinned prices are ac

### SG-001 — TractorFacet omits Invariable fundsSafu net that sibling entrypoints enforce
- **Severity:** Medium  ·  **Status:** submit  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/farm/TractorFacet.sol :: tractor
- **Impact:** Defense-in-depth solvency loss on the tractor path. Each inner delegatecall into a guarded facet (deposit/withdraw/convert/claim) re-checks `fundsSafu` at its own boundary, so a single inner call cannot leave the protocol insolvent. The residual exposure is that tractor executes a publisher-authoriz
- **Decision:** Confirmed: TractorFacet does not inherit Invariable (FarmFacet and DepotFacet do, with fundsSafu), yet tractor() executes an arbitrary AdvancedFarmCall[] batch as the publisher with only verifyRequisition+runBlueprint and no wrapper-level fundsSafu/flow guard. Inner guarded facets re-check fundsSafu

### AC-003 — LibTractor domain separator uses wrong typehash (BLUEPRINT not EIP712Domain)
- **Severity:** Low  ·  **Status:** submit  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/libraries/LibTractor.sol :: _domainSeparatorV4
- **Impact:** Non-standard EIP-712 domain separator: signatures from standard tooling will not verify against Tractor blueprints. No auth bypass, no replay (chainId present, per-blueprint nonce enforced). Severity Low (standards/interoperability correctness).
- **Decision:** Confirmed: LibTractor._domainSeparatorV4 uses BLUEPRINT_TYPE_HASH as the domain typehash instead of the defined EIP712_TYPE_HASH, producing a non-standard domain separator. No auth bypass/replay results: the same non-standard separator is used by both signer-recovery and verifier, chainId is include


## Human-review queue

### CC-001 — L1->L2 migration redemption has no spent-marker and uses += accounting, allowing unbounded replay of a single proof/signature to mint unbacked deposits, stalk and roots
- **Severity:** Critical  ·  **Status:** poc_required  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/silo/L2ContractMigrationFacet.sol :: redeemDepositsAndInternalBalances
- **Impact:** An attacker observes any legitimate migration redemption (or front-runs one), then replays the identical calldata repeatedly. stalk and roots are inflated without backing on each replay; stalk and roots are the governance vote weight and the divisor/numerator for earned-Bean (mint) distribution. Unb
- **Decision:** Confirmed in source: redeemDepositsAndInternalBalances (L88-114) verifies a static Merkle proof + EIP-712 sig but writes NO spent/nonce marker; setStalk (L206-207) uses += for stalk and roots. Proof+signature are public calldata, so the identical call is replayable until deadline, each replay re-add

### CC-002 — BeanL1RecieverFacet caps migrated L1 Beans at EXTERNAL_L1_BEANS = 0, so every L2 mint reverts after the user's L1 Beans are already burned (permanent cross-chain fund loss)
- **Severity:** High  ·  **Status:** submit  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/migration/BeanL1RecieverFacet.sol :: recieveL1Beans
- **Impact:** Direct, permanent loss of all externally-held L1 Beans that attempt migration: L1 burn succeeds, the corresponding L2 mint always reverts because the migration cap is 0. No attacker is required; the migration path is fully bricked and every user who uses it loses funds. Critical under Immunefi v2.2 
- **Decision:** Confirmed in source: BeanL1RecieverFacet EXTERNAL_L1_BEANS=0 (L22); recieveL1Beans does migratedL1Beans += amount then require(EXTERNAL_L1_BEANS >= migratedL1Beans) (L40), i.e. require(0 >= positive), always false for amount>0, so C.bean().mint (L43) is unreachable. The companion L1 path burns Beans

### CC-003 — Migration Merkle leaf omits reciever, so any holder of the public L1 signature can redirect another contract's migration credit to an attacker-chosen L2 address
- **Severity:** High  ·  **Status:** poc_required  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/silo/L2ContractMigrationFacet.sol :: verifyDepositsAndInternalBalances
- **Impact:** The migration deposit/stalk/roots credit for an L1 contract can be redirected to and/or duplicated at an attacker-chosen L2 address using the publicly visible signature, rather than only the originally intended reciever. Standalone this is an authorization-binding gap; combined with CC-001 it conver
- **Decision:** Confirmed: verifyDepositsAndInternalBalances leaf = keccak256(account, deposits, internalBalances, ownerRoots) (L127) omits reciever; destination is bound only by the EIP-712 signature (L144), which is public calldata. The immutable MERKLE_ROOT never constrains the L2 destination. Standalone a weak 

### LG-001 — L2ContractMigrationFacet zeroes global per-token silo balances on every redeem
- **Severity:** High  ·  **Status:** poc_required  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/silo/L2ContractMigrationFacet.sol :: addMigratedDepositsToAccount
- **Impact:** Global deposited/depositedBdv for every token routed through contract migration is set to 0 while per-account deposits exist, breaking the core invariant total == sum(accounts) (ACC-002). Downstream consumers that read s.sys.silo.balances[token] for BDV ratios, convert valuation, gauge weighting and
- **Decision:** Confirmed in source: addMigratedDepositsToAccount declares uint128 totalDeposited/totalDepositedBdv (L159-160), never increments them, then writes them to s.sys.silo.balances[token].deposited/.depositedBdv (L194-195) -- always 0 -- on every permissionless redeem. Hard assignment clobbers any prior R

### BSA-001 — LibChainlinkOracle.getTokenPrice NatSpec states lookback>0 returns TWAP, but the ternary returns spot for lookback>0 and divides-by-zero for lookback==0
- **Severity:** Medium  ·  **Status:** submit  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/libraries/Oracle/LibChainlinkOracle.sol :: getTokenPrice
- **Impact:** Any internal consumer that follows the documented convention and passes lookback>0 expecting manipulation resistance instead consumes the instantaneous spot price. If a reachable mint/convert/peg path (LibEthUsdOracle -> LibWellMinting/LibDeltaB -> sunrise Bean issuance / convert valuation) requests
- **Decision:** Confirmed in source (LibChainlinkOracle.getTokenPrice L45-47): `lookback > 0 ? getPrice(...) : getTwap(..., lookback)` is inverted vs NatSpec (L34-37: lookback>0 = TWAP). A TWAP request returns spot; a spot request calls getTwap(...,0) which divides by lookback=0 (revert), also breaking the document

### BSA-005 — ReseedBarn struct @dev 'fertilizerIds MUST be in acsending order' is never enforced in mintFertilizers, allowing a malformed nextFid linked list
- **Severity:** Medium  ·  **Status:** submit  ·  **Confidence:** High
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/init/reseed/L2/ReseedBarn.sol :: mintFertilizers
- **Impact:** A non-ascending or duplicate-id input yields a malformed/cyclic fertilizer linked list. Sun fertilizer payout traverses nextFid in id order to pay Beans to fertilizer holders; a corrupted chain strands or mispays fertilizer (holders past the break never get paid, or a cycle disrupts iteration). Boun
- **Decision:** Confirmed: ReseedBarn.mintFertilizers builds the nextFid linked list (fertFirst, nextFid[prev]=cur, fertLast) assuming ascending fertilizerIds, a 'MUST' stated only in NatSpec and never enforced. Out-of-order/duplicate input produces a malformed/cyclic list that strands or mispays Sun fertilizer pay

### CC-005 — Migration EIP-712 domain separator hardcodes L1 chainId and lacks any per-message nonce or destination-L2 binding, enabling cross-deployment/multi-L2 signature reuse
- **Severity:** Medium  ·  **Status:** submit  ·  **Confidence:** Medium
- **Location:** contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/silo/L2ContractMigrationFacet.sol :: _domainSeparatorV4
- **Impact:** Cross-deployment / multi-L2 replay of a single migration signature and absence of a nonce that would otherwise bound CC-001. On a single-L2 deployment the practical impact is subsumed by CC-001; the standalone severity (signature not scoped to destination chain + no nonce) is Medium. The hardcoded l
- **Decision:** Confirmed: the migration EIP-712 domain uses C.getLegacyChainId() (hardcoded 1) and address(this), and the struct hash covers only (owner, reciever, deadline) -- no nonce and no destination-L2 binding. A single owner signature is valid on any L2 deployment sharing the diamond address and the hardcod
