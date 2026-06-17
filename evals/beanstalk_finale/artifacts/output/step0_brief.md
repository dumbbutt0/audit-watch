# Step 0 Analysis Brief — beanstalk-2024-05-eval2
Generated: 2026-05-29 20:25 UTC

## Summary
Total threads: 15  (Critical: 0 · High: 7 · Medium: 5 · NEEDS_MORE_CONTEXT: 3)
Threads escalated to findings: 0
Soft-flag threads (score=3 watch list): 0

## Priority Thread Ranking

### ⚪ Score 0

#### [T-001] (no title)  `HIGH_THREAD`
- **Invariant**: ACC-001  · **Chain**: CH-002
- **Functions**: `reseedSiloDeposit()`, `accountStalk_bean()`, `accountStalk_beanEth()`
- **Entry conditions**: Migration upgrade executed: ReseedSilo.init runs reseedSiloDeposit once per whitelisted token. Any account that held deposits in 2+ tokens on L1 (e.g. Bean AND BEAN:ETH).

#### [T-002] (no title)  `HIGH_THREAD`
- **Invariant**: ACC-002  · **Chain**: CH-001
- **Functions**: `totalDepositedBdv()`, `totalDeposited()`
- **Entry conditions**: A contract account redeems via L2ContractMigrationFacet.redeemDepositsAndInternalBalances with a valid merkle proof + signature.

#### [T-003] (no title)  `HIGH_THREAD`
- **Invariant**: ACC-003  · **Chain**: CH-001
- **Functions**: `redeemDepositsAndInternalBalances()`, `passes()`
- **Entry conditions**: Attacker obtains one valid (owner, deposits, proof) leaf and the owner's EIP-712 signature over (owner, reciever, deadline) before deadline. Signature/proof are public once submitted on-chain.
- ⚠️ **Domain flag**: Cross-Chain — keywords: nonce

#### [T-004] (no title)  `HIGH_THREAD`
- **Invariant**: STATE-001  · **Chain**: CH-003
- **Functions**: `for()`
- **Entry conditions**: ReseedField.init invoked during migration with any account having >=1 plot.

#### [T-005] (no title)  `HIGH_THREAD`
- **Invariant**: ACC-004  · **Chain**: CH-004
- **Functions**: `recieveL1Beans()`, `amount()`, `require()`
- **Entry conditions**: External L1 Bean holder burns Beans on L1 via BeanL2MigrationFacet.migrateL2Beans; bridge relays recieveL1Beans on L2.
- ⚠️ **Domain flag**: Cross-Chain — keywords: bridge

#### [T-006] (no title)  `HIGH_THREAD`
- **Invariant**: ARITH-001  · **Chain**: CH-005
- **Functions**: `getTokenPrice()`, `getPrice()`, `getTwap()`, `price()`, `lookback()`
- **Entry conditions**: Any code path that requests a manipulation-resistant TWAP price via LibChainlinkOracle.getTokenPrice(addr, timeout, lookback>0).
- ⚠️ **Domain flag**: Oracle / Price — keywords: getprice, twap, gettwap

#### [T-013] (no title)  `HIGH_THREAD`
- **Invariant**: CC-001  · **Chain**: CH-001
- **Functions**: `only()`, `signature()`, `replay()`
- **Entry conditions**: Same as T-003; merkle leaf = keccak256(account, deposits, internalBalances, ownerRoots) — does NOT include reciever.

#### [T-007] (no title)  `MEDIUM_THREAD`
- **Invariant**: ARITH-003  · **Chain**: CH-005
- **Functions**: `uint256()`, `div()`
- **Entry conditions**: A frozen/broken Chainlink feed during a price query that flows through LibUsdOracle.getUsdPrice/getTokenPriceFromExternal.
- ⚠️ **Domain flag**: Oracle / Price — keywords: oracle, chainlink

#### [T-008] (no title)  `MEDIUM_THREAD`
- **Invariant**: CC-003  · **Chain**: CH-008
- **Functions**: `staticcall()`, `mload()`, `add()`
- **Entry conditions**: A token whose oracleImplementation has a custom (non-0x01/0x02) encodeType and a target contract.
- ⚠️ **Domain flag**: Oracle / Price — keywords: oracle

#### [T-009] (no title)  `MEDIUM_THREAD`
- **Invariant**: ACC-010  · **Chain**: CH-002
- **Functions**: `init()`
- **Entry conditions**: Post-ReseedSilo: compare SUM(account stalk) to s.sys.silo.stalk.

#### [T-014] (no title)  `MEDIUM_THREAD`
- **Invariant**: ACC-005  · **Chain**: CH-009
- **Entry conditions**: ReseedInternalBalances.init called with farmers[] and balances[] of unequal length.

#### [T-015] (no title)  `MEDIUM_THREAD`
- **Invariant**: ACC-007  · **Chain**: CH-010
- **Entry conditions**: ReseedBarn.init given fertilizerIds NOT in ascending order (contract comment requires ascending but code does not enforce).
- ⚠️ **Domain flag**: DEX / AMM — keywords: mint

## NEEDS_MORE_CONTEXT (Requires Domain Knowledge)

- **[T-010]** (no title)
  - Invariant: CC-004
- **[T-011]** (no title)
  - Invariant: STATE-002
  - Domain flags: Cross-Chain
- **[T-012]** (no title)
  - Invariant: STATE-004

## Function Heatmap

| Function | Threads | Max severity | Domain flags |
|----------|---------|--------------|--------------|
| `reseedSiloDeposit()` | 1 | High | - |
| `accountStalk_bean()` | 1 | High | - |
| `accountStalk_beanEth()` | 1 | High | - |
| `totalDepositedBdv()` | 1 | High | - |
| `totalDeposited()` | 1 | High | - |
| `redeemDepositsAndInternalBalances()` | 1 | High | Cross-Chain |
| `passes()` | 1 | High | Cross-Chain |
| `for()` | 1 | High | - |
| `recieveL1Beans()` | 1 | High | Cross-Chain |
| `amount()` | 1 | High | Cross-Chain |
| `require()` | 1 | High | Cross-Chain |
| `getTokenPrice()` | 1 | High | Oracle / Price |
| `getPrice()` | 1 | High | Oracle / Price |
| `getTwap()` | 1 | High | Oracle / Price |
| `price()` | 1 | High | Oracle / Price |
| `lookback()` | 1 | High | Oracle / Price |
| `uint256()` | 1 | Medium | Oracle / Price |
| `div()` | 1 | Medium | Oracle / Price |
| `staticcall()` | 1 | Medium | Oracle / Price |
| `mload()` | 1 | Medium | Oracle / Price |

## Domain Pattern Alerts

- **Cross-Chain**: T-003, T-005, T-011 — keywords: nonce
- **DEX / AMM**: T-015 — keywords: mint
- **Oracle / Price**: T-006, T-007, T-008 — keywords: getprice, twap, gettwap
