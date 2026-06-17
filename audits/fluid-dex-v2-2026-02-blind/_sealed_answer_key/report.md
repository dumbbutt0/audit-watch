# Issue H-1: User can steal funds using `_processNormalSupplyAction` uncapped withdrawal 

Source: https://github.com/sherlock-audit/2026-01-fluid-dex-v2-judging/issues/610 

## Found by 
0x04, 0x23r0, 0x37, 0xBoraichoT, 0xCrypt0nite, 0xSeerBear, 0xShoonya, 0xastronatey, 0xbzbee42, 0xpetern, AV, Baazigar, Bigsam, Billy19d, Bizarro, Blackdruid, BogdanCastraveti, Draxen, EddiePumpin, Edoscoba, ElmInNyc99, Frontrunner, I1iveF0rTh1Sh1t, Icon\_0x, Leaningone, Merlinsan, Proof-of-Spirit, Riceee, Ridden5839, SecurityAgentOZ, Thisisit, Waydou, Wojack, ZeroTrust, axelot, botdidy, bratwork, crab0saurus, crunter, elolpuer, ff4de, fgh56ty, fuzious, gabkov, gh0xt, hirusha, i-am-kuldeep, iamephraim, lanrebayode77, legat, luc1jan, maigadoh, neeloy, nonso72, oct0pwn, pranamya, rajatbeladiya, slowpoke, thimthor, vivekd, xiaoming90

### Summary

In [`contracts/protocols/moneyMarket/core/operateModule/helpers.sol`](https://github.com/sherlock-audit/2026-01-fluid-dex-v2/blob/52ec6be99521c26ecb433c92ec9e1fb18c380a4a/fluid-contracts/contracts/protocols/moneyMarket/core/operateModule/helpers.sol#L459), `_processNormalSupplyAction` caps the `withdrawalAmountRaw` to the `totalRawSupply` of the user's position, but does not cap the user's withdrawal amount specified (`supplyAmount`) based on the `totalRawSupply` of the user's position (the amount user has previously supplied).

Hence, users can withdraw more than they supplied, protocol loss of funds.

### Root Cause

In [`contracts/protocols/moneyMarket/core/operateModule/helpers.sol`](https://github.com/sherlock-audit/2026-01-fluid-dex-v2/blob/52ec6be99521c26ecb433c92ec9e1fb18c380a4a/fluid-contracts/contracts/protocols/moneyMarket/core/operateModule/helpers.sol#L459), `_processNormalSupplyAction` caps the `withdrawalAmountRaw` to the `totalRawSupply` of the user's position, but does not cap the user's withdrawal amount specified (`supplyAmount`) based on the `totalRawSupply` of the user's position (the amount user has previously supplied).

```javascript
            if (supplyAmount_ == type(int256).min) {
                ...<SNIP>...
            } else {
                withdrawAmountRaw_ = (((uint256(-supplyAmount_) * LC.EXCHANGE_PRICES_PRECISION) + 1) / supplyExchangePrice_) + 1; // rounded up so protocol is on the winning side
@>              if (withdrawAmountRaw_ > tokenRawSupply_) withdrawAmountRaw_ = tokenRawSupply_; // added this check for safety
            }
```

### Internal Pre-conditions

N/A

### External Pre-conditions

N/A

### Attack Path

Conditions of example:
1. Current `supplyExchangePrice` is 1e12

Example:
1. User creates a normal supply position and supplies a minimum amount (e.g. 1e6) of tokens. `tokenRawSupply` of user's `_positionData` is populated as follows. User now has an NFT and a position in the NFT
```javascript
// tokenRawSupply_ = ((uint256(supplyAmount_) * LC.EXCHANGE_PRICES_PRECISION) - 1) / supplyExchangePrice_;
// if (tokenRawSupply_ > 0) tokenRawSupply_ -= 1;

_positionData[][].tokenRawSupply = (((1e6 * 1e12) - 1) / 1e12) - 1 = 999998
```

2. User withdraws from the above position with `supplyAmount` of -1000e18 (or any amount > type(int256).min). This is more than what the user has supplied. In `_processNormalSupplyAction`, `withdrawAmountRaw_` is greater than `totalRawSupply` of the user's position, so it will be capped, and `_updateStorageForWithdraw` deletes user's `_positionData`. 

```javascript
// if (supplyAmount_ == type(int256).min) {
// } else {
//     withdrawAmountRaw_ = (((uint256(-supplyAmount_) * LC.EXCHANGE_PRICES_PRECISION) + 1) / supplyExchangePrice_) + 1;
//     if (withdrawAmountRaw_ > tokenRawSupply_) withdrawAmountRaw_ = tokenRawSupply_;
// }

withdrawAmountRaw_ = (((-(-1000e18) * 1e12) + 1) / 1e12) + 1 
                   = 1000000000000000000001
                   = 999998 // capped to user's totalRawSupply
```

3. However, `supplyAmount` is not correspondingly capped based on the `totalRawSupply` of the user's position. Thereafter, `_processNormalSupplyAction` calls `LIQUIDITY.operate` to transfer 1000e18 of tokens to user.

```javascript
LIQUIDITY.operate(token_, supplyAmount_, 0, to_, address(0), abi.encode(MONEY_MARKET_IDENTIFIER, NORMAL_WITHDRAW_ACTION_IDENTIFIER));
// supplyAmount not capped based on `totalRawSupply` of the user's position
// supplyAmount is still -1000e18 at this point
```

4. User supplied 1e6 tokens but withdraws 1000e18 tokens. User withdraws more than they supplied, protocol loss of funds.

### Impact

1. User withdraws more than they supplied
2. Protocol loss of funds 

### PoC

Refer attack path

### Mitigation

If `withdrawAmountRaw_` exceed `tokenRawSupply_`, cap the `supplyAmount` based on the `tokenRawSupply_`

```diff
            } else {
                withdrawAmountRaw_ = (((uint256(-supplyAmount_) * LC.EXCHANGE_PRICES_PRECISION) + 1) / supplyExchangePrice_) + 1; // rounded up so protocol is on the winning side
-               if (withdrawAmountRaw_ > tokenRawSupply_) withdrawAmountRaw_ = tokenRawSupply_; // added this check for safety
+               if (withdrawAmountRaw_ > tokenRawSupply_){
+                   withdrawAmountRaw_ = tokenRawSupply_;
+                   uint256 withdrawAmount_ = ((tokenRawSupply_ * supplyExchangePrice_) - 1) / LC.EXCHANGE_PRICES_PRECISION;
+                   if (withdrawAmount_ > 0) withdrawAmount_ -= 1;
+                   supplyAmount_ = -int256(withdrawAmount_);
+               }
            }
```

# Issue M-1: Liquidity-layer failure fallback stores owed payouts under `to_`, making withdrawals/borrows/fees permanently unclaimable for EOAs 

Source: https://github.com/sherlock-audit/2026-01-fluid-dex-v2-judging/issues/1111 

## Found by 
0xastronatey, 4Nescient, AV, Bizarro, Diavolo, Draxen, Emmanuel, ExtraCaterpillar, Harry-Elite, Jiberish, Kenn.eth, Leaningone, LeoGold, Pelz, Proof-of-Spirit, SarveshLimaye, Waydou, ZeroTrust, botdidy, edantes, fullcounterhunter, fuzious, gabkov, gh0xt, jo13, jongwon, legat, lodelux, natachi, neeloy, nitinaimshigh, rajatbeladiya, thimthor, uba, xiaoming90, yaioxy

### Summary

The Liquidity-layer failure fallback in `FluidDexV2.settle()` credits `_userStoredTokenAmount` to `to_` while all redemption is keyed to `msg.sender` and gated behind `startOperation`, which will cause a permanent loss of owed payouts for recipients as any Liquidity-layer revert during a net-out settlement will silently replace the transfer with an unclaimable “stored” balance.

### Root Cause

- In `contracts/contracts/protocols/dexV2/base/core/main.sol:189` the Liquidity-failure fallback credits stored balances to `to_` instead of the only redeemable key (`msg.sender`):
  - `_userStoredTokenAmount[BASE_SLOT][to_][token_] += uint256(-netAmount_);`
- In `contracts/contracts/protocols/dexV2/base/core/helpers.sol:60-67` stored-balance accounting (store/unstore) is exclusively keyed to `msg.sender`, meaning only `msg.sender` can ever reduce/withdraw a stored balance:
  - `int256(_userStoredTokenAmount[BASE_SLOT][msg.sender][token_]) + storeAmount_`
- In `contracts/contracts/protocols/dexV2/base/core/main.sol:20-33` and `contracts/contracts/protocols/dexV2/base/core/main.sol:80` the only callable path to `settle()` is via callback-gated `startOperation()` + `_onlyAfterOperationStarted`, preventing EOAs (and most non-callback contracts) from redeeming any stored credit keyed to their address.

### Internal Pre-conditions

-

### External Pre-conditions

-

### Attack Path

`FluidDexV2.settle()` is designed to support “store instead of transfer” behavior when the Liquidity layer interaction fails. Concretely, `settle()` computes:

- `netSupplyAmount_ = supplyAmount_ + storeAmount_`
- `netAmount_ = netSupplyAmount_ - borrowAmount_`

When `netAmount_ < 0`, the DEX is supposed to **pay tokens out** to `to_`.

If the contract has enough on-hand balance, it transfers directly. Otherwise it calls `_callLiquidityLayer(...)`, which wraps `LIQUIDITY.operate(...)` in a `try/catch` and returns `false` on revert. When `_callLiquidityLayer(...)` returns `false`, `settle()` enters a fallback branch.

### The intended behavior vs. actual behavior

In the fallback branch for `netAmount_ < 0`, the code explicitly states it will “store the amount in the contract so the user can withdraw later”, but it stores it under:

- `_userStoredTokenAmount[...][to_][token_]`

This is incompatible with how stored balances are ever consumed:

- Stored balances are only updated/consumed for `_userStoredTokenAmount[...][msg.sender][token_]` inside `_updateSettledAmountsOnStorage()`.

There is no separate withdrawal function for `_userStoredTokenAmount[...][addr][token_]`, and there are no other code paths that debit `_userStoredTokenAmount` for an arbitrary owner.

### Why this permanently strands funds for typical recipients

Even if the storage key were correct, redemption is further constrained by access pattern:

- `settle()` is protected by `_onlyAfterOperationStarted` (must be within an active operation).
- The only way to create an active operation is `startOperation()`, which calls back into `msg.sender` via `IDexV2Callbacks(msg.sender).startOperationCallback(data_)`.

As a result:

- EOAs cannot successfully use `startOperation()` (they do not implement the callback ABI), so they cannot reach a state where they can call `settle()`.
- Even callback-capable routers (e.g., MoneyMarket) cannot redeem balances stored under the recipient key, because redemption is keyed to `msg.sender`, not `to_`.

So when Liquidity fails and a payout is stored to `to_` (commonly an EOA), the system produces an internal IOU that the credited address cannot practically claim, and no other party can claim on their behalf.

### Realistic triggering contexts in this codebase

MoneyMarket is built around a router/callback pattern where the router (`MoneyMarket`) is the `msg.sender` to DexV2, and the end recipient `to_` is user-provided (usually an EOA). In multiple core flows, MoneyMarket calls `DEX_V2.settle(..., to_=to_)`:

- Fee collection (`_feeSettle`, called from callback module)
- Withdraw settlements (`_withdrawSettle`)
- Borrow settlements (`_borrowSettle`)
- Liquidation withdrawals and fee claims (LiquidateModule sets `params_.to` as the payout recipient)

Because `DexV2.settle()` does not revert on Liquidity failure (it stores instead), the higher-level MoneyMarket flow will continue executing and update its own bookkeeping (e.g., stored fee accounting, position deletion, debt changes), while the recipient never receives tokens and cannot redeem the stored credit. This silently converts “success” into unrecoverable loss.

https://github.com/sherlock-audit/2026-01-fluid-dex-v2/blob/main/fluid-contracts/contracts/protocols/moneyMarket/core/operateModule/main.sol#L1

## Attack Path

### Path 1 — Any net-out `DexV2.settle()` where Liquidity reverts and `to_` is an EOA

1. A callback-capable integrator contract calls `FluidDexV2.startOperation(...)`. (`contracts/contracts/protocols/dexV2/base/core/main.sol:20-33`)
2. Inside `startOperationCallback`, the integrator calls `FluidDexV2.settle(..., to_ = recipientEOA, ...)` in a context where `netAmount_ < 0` (protocol must pay tokens out). (`.../dexV2/base/core/main.sol:117-119`)
3. `_callLiquidityLayer(...)` attempts `LIQUIDITY.operate(...)` but reverts; the `try/catch` returns `false`. (`.../dexV2/base/core/helpers.sol:70+`)
4. `settle()` enters the fallback branch and skips the transfer, instead incrementing `_userStoredTokenAmount[...][recipientEOA][token_]`. (`.../dexV2/base/core/main.sol:181-193`)
5. The operation completes successfully, but `recipientEOA` cannot later run the callback-gated flow required to call `settle()` as `msg.sender`, so the credited amount is effectively permanently unclaimable.

### Path 2 — MoneyMarket fee collection converts earned fees into an unclaimable stored balance

1. User triggers fee collection and sets `to_ = userEOA` in `actionData`. (`contracts/contracts/protocols/moneyMarket/core/callbackModule/main.sol:48-114`)
2. MoneyMarket updates `_positionFeeStored` by subtracting the user’s requested `feeCollectionAmount` (fees are considered “collected” in MoneyMarket accounting). (`.../moneyMarket/core/callbackModule/helpers.sol:69-91`)
3. MoneyMarket calls `_feeSettle(...)`, which calls `DEX_V2.settle(token, -feeAccrued, 0, feeAccrued-feeCollected, to_=userEOA, ...)` making `netAmount = -feeCollected` (net-out payout). (`.../moneyMarket/core/callbackModule/helpers.sol:9-14`)
4. If Liquidity reverts, DexV2 stores `feeCollected` under `userEOA` and skips the transfer. (`.../dexV2/base/core/main.sol:181-193`)
5. User’s fees are now **decremented in MoneyMarket** and the DexV2 credit is **unredeemable**, so the user loses their fee payout.

### Path 3 — MoneyMarket D3 withdraw: principal + accrued fees can be “withdrawn” on-chain but never delivered

1. User withdraws from a D3 position and sets `to_ = userEOA`. (`.../moneyMarket/core/callbackModule/main.sol:256-327`)
2. MoneyMarket executes the DEX withdraw (`DEX_V2.operate(...)`) then calls `_withdrawSettle(...)` for each token. (`.../moneyMarket/core/callbackModule/main.sol:263-297`)
3. `_withdrawSettle` calls `DEX_V2.settle(token, -(amount+feeAccrued), 0, feeAccrued, to_=userEOA, ...)` producing a net-out payout. (`.../moneyMarket/core/callbackModule/helpers.sol:17-21`)
4. If Liquidity reverts, DexV2 stores the owed payout under `userEOA` and skips the transfer. (`.../dexV2/base/core/main.sol:181-193`)
5. MoneyMarket continues execution (fee storage update, caps update, potential position deletion), so the withdrawal cannot be simply retried and the user never receives the withdrawn assets.

### Path 4 — MoneyMarket D4 borrow: debt can be increased without the borrower receiving the borrowed tokens

1. User borrows from a D4 position with `to_ = userEOA`. (`.../moneyMarket/core/callbackModule/main.sol:331-403`)
2. MoneyMarket executes the borrow (`DEX_V2.operate(...)`) then calls `_borrowSettle(...)`. (`.../moneyMarket/core/callbackModule/main.sol:340-375`)
3. `_borrowSettle` calls `DEX_V2.settle(token, -feeAccrued, amount, feeAccrued, to_=userEOA, ...)` resulting in `netAmount = -amount` (net-out borrowed tokens). (`.../moneyMarket/core/callbackModule/helpers.sol:23-27`)
4. If Liquidity reverts, DexV2 stores the owed borrowed amount under `userEOA` and skips the transfer. (`.../dexV2/base/core/main.sol:181-193`)
5. The borrow-side state changes remain, but the borrower does not receive the borrowed funds and cannot redeem them, potentially cascading into liquidations due to increased debt without corresponding assets.

### Path 5 — Liquidation payouts can be silently converted into unclaimable credits, breaking liquidation incentives

1. A liquidator calls `LiquidateModule` and sets `params_.to` (defaults to `msg.sender`, typically an EOA). (`contracts/contracts/protocols/moneyMarket/core/liquidateModule/main.sol:50`)
2. Liquidation performs withdraw and/or fee-collection operations where `actionData` includes `params_.to`, causing the callback module to ultimately call settlement helpers that pay out to that `to_`. (`.../liquidateModule/main.sol:468-494`, `.../liquidateModule/main.sol:610-611`)
3. If Liquidity reverts during the resulting net-out `DexV2.settle(...)`, DexV2 stores the liquidator’s payout under their EOA and skips the transfer. (`.../dexV2/base/core/main.sol:181-193`)
4. The liquidation flow can proceed updating protocol state, while the liquidator never receives the payout and cannot redeem it, making liquidations unreliable and potentially non-functional under the exact failure conditions this fallback was meant to handle.

### Impact

Affected users and liquidators can suffer an approximate loss of up to 100% of any net-out token amount that hits the Liquidity-failure fallback (withdrawn principal, borrowed assets, and/or collected fees), because the protocol records the payout under `_userStoredTokenAmount[to_]` but provides no viable redemption path for EOAs (or non-callback recipients).

- Users can lose withdrawal proceeds (principal + any included fee accrual) when a D3 withdraw settlement hits the fallback.
- Users can lose borrowed assets (while still taking on the debt-side state changes) when a D4 borrow settlement hits the fallback.
- Users can lose accrued fee payouts because MoneyMarket debits `_positionFeeStored` before calling `DexV2.settle()`, and the fallback does not revert—so the fee entitlement is reduced even though the payout is never delivered.
- Liquidators can lose liquidation proceeds (and therefore liquidation incentives collapse under these failure conditions), which can break the protocol’s ability to resolve unhealthy positions whenever the Liquidity layer reverts.

### PoC

_No response_

### Mitigation

_No response_

# Issue M-2: Liquidation uses DexV2 spot price to derive D3 collateral composition and weighted penalties, enabling MEV over-seizure 

Source: https://github.com/sherlock-audit/2026-01-fluid-dex-v2-judging/issues/1114 

## Found by 
0x37, 6PottedL, AV, Baazigar, Bizarro, Kalyan\_\_tr, Laksmana, Rizalfahmi, Silvermist, Slayer, ZeroTrust, hexnikk, pashap9990, thimthor, velev, xiaoming90, yonko

### Summary

The reliance on DexV2 pool spot state (`sqrtPriceX96`/`currentTick`) when computing D3/D4 liquidation withdrawals will cause excessive collateral seizure for liquidated borrowers as MEV liquidators will sandwich the pool price around `liquidate()` to skew LP composition, accrued fees, and the value-weighted liquidation penalty in their favor.

### Root Cause

- In `protocols/moneyMarket/core/liquidateModule/main.sol:369-423` the liquidation path for `D3_POSITION_TYPE` derives `token0SupplyAmount`/`token1SupplyAmount` using `sqrtPriceX96: AT_POOL_PRICE`, then computes `averageLiquidationPenalty_` from those spot-derived amounts and scales `withdrawValue` by that average penalty.
- In `protocols/moneyMarket/core/other/helpers.sol:467-470` `_getD3SupplyAmounts` treats `AT_POOL_PRICE` as a sentinel and reads the current pool `sqrtPriceX96` directly from DexV2 packed variables, making liquidation-time collateral decomposition depend on manipulable spot price.
- In `protocols/moneyMarket/core/other/helpers.sol:418-439` `_getDexV2FeeAccruedAmounts` uses the current pool tick from DexV2 variables to compute fee growth “inside” the range; liquidation consumes these spot-tick-dependent accrued fees in both:
  - D3 liquidation fee handling (`protocols/moneyMarket/core/liquidateModule/main.sol:383-385` and `main.sol:481-501`), and
  - D4 liquidation fee withdrawal (`protocols/moneyMarket/core/liquidateModule/main.sol:563-579`).

### Internal Pre-conditions

-

### External Pre-conditions

-

### Attack Path

D3 collateral positions represent concentrated-liquidity (CL) liquidity in a DexV2 pool over a tick range. For CL positions, the instantaneous split of the position between token0 and token1 is a function of the current pool price: pushing price toward one end of the range makes the position hold almost entirely one token, while pushing price toward the other end makes it hold mostly the other token.

In the D3 liquidation withdraw branch, the protocol intentionally passes `sqrtPriceX96: AT_POOL_PRICE` into `_getD3SupplyAmounts`, which forces the helper to read the current pool `sqrtPriceX96` from DexV2 storage. Those spot-derived amounts are then valued with oracle prices and used to compute `averageLiquidationPenalty_` as a value-weighted average of the two token liquidation penalties. Finally, `withdrawValue` (the amount of collateral value to seize for a given payback value) is scaled up by `averageLiquidationPenalty_`.

This creates a liquidation-time dependency on a permissionless, manipulable input: any MEV actor can move the DexV2 pool price/tick via swaps in the same block and then call `liquidate()`. By doing so, the liquidator can:

- Change the D3 position’s liquidation-time token composition (token0 vs token1 amounts).
- Change the value-weighted liquidation penalty (since the weights depend on the manipulated composition, and token penalties can differ).
- Change which token(s) are actually withdrawn (because the withdrawal amounts are computed from the spot-derived token amounts and `withdrawValue`).

Additionally, liquidation reads and withdraws D3/D4 fees based on spot tick via `_getDexV2FeeAccruedAmounts`. If the liquidator’s pre-liquidation swap activity generates fees while the victim position is in-range, those newly accrued fees can be immediately accounted for and (depending on how much of `withdrawValue` remains after principal withdrawal, or in the D4 fee-withdraw branch) seized as part of the liquidation withdrawal. This “fee recycling” reduces the effective cost of manipulating the pool state and amplifies the profitability and reliability of the sandwich.

Critically, the protocol’s liquidation eligibility is gated by health factor calculations that use an oracle-implied sqrt price for D3/D4 valuation, not the pool spot price (see `_getHfInfo` using `_calculateSqrtPriceX96` and passing that into `_getD3SupplyAmounts/_getD4DebtAmounts` in `protocols/moneyMarket/core/other/helpers.sol:899-920` and `helpers.sol:974-997`). As a result, a liquidator can manipulate pool spot price aggressively without needing to manipulate the oracle-based HF check, making this a clean MEV surface focused on liquidation extraction rather than liquidation eligibility.

https://github.com/sherlock-audit/2026-01-fluid-dex-v2/blob/main/fluid-contracts/contracts/protocols/moneyMarket/core/operateModule/main.sol#L1

## Attack Path

### Attack path 1 — Inflate the value-weighted D3 liquidation penalty by skewing spot composition

1. MEV liquidator monitors for a liquidatable NFT whose chosen withdraw position is `D3_POSITION_TYPE`, and where the effective per-token liquidation penalties differ.
2. Liquidator front-runs with a swap in the relevant DexV2 pool to move `sqrtPriceX96/currentTick` toward the end of the victim’s tick range that makes the D3 position hold mostly the higher-penalty token at that instant.
3. Liquidator calls `FluidMoneyMarketLiquidateModule.liquidate()` selecting that D3 position as `withdrawPositionIndex`.
4. The module calls `_getD3SupplyAmounts(... sqrtPriceX96: AT_POOL_PRICE)` (`liquidateModule/main.sol:369-381`), which reads the manipulated pool spot price (`other/helpers.sol:467-470`) and returns a skewed `token0SupplyAmount/token1SupplyAmount`.
5. The module computes `averageLiquidationPenalty_` using oracle-valued weights derived from the manipulated composition and scales `withdrawValue` upward (`liquidateModule/main.sol:408-423`).
6. The liquidation withdraws a larger amount of collateral value (and/or a more favorable token composition) than would be possible at an unmanipulated pool price, transferring additional value from borrower to liquidator.
7. Liquidator back-runs with the inverse swap to restore pool price and realizes net MEV profit (or uses the seized collateral to unwind the initial manipulation).

### Attack path 2 — Token mix steering to maximize realized liquidation profit even without large penalty differences

1. Liquidator chooses a swap direction that makes the D3 position’s liquidation-time composition concentrate into the token the liquidator prefers to receive (e.g., more liquid to unwind, less volatile to hold, or easier to source/hedge).
2. Liquidator calls `liquidate()` while the pool remains in the manipulated state.
3. Because withdrawal amounts are computed from the spot-derived token amounts, the liquidation withdraws collateral predominantly in that preferred token.
4. Liquidator reduces external swap/slippage costs required to realize profit from the seized collateral, increasing effective extraction versus liquidation at the unmanipulated spot.

### Attack path 3 — Fee-recycling sandwich using spot-tick-dependent fee accrual (D3 and D4)

1. Liquidator performs a pre-liquidation swap (or a sequence of swaps) that moves price/tick and pays swap fees to in-range liquidity that includes the victim’s D3/D4 position.
2. `other/helpers.sol:_getDexV2FeeAccruedAmounts` computes fees “inside” the victim range using the current tick (`helpers.sol:418-439`), so the just-paid fees become immediately attributable as `feeAccruedToken0/feeAccruedToken1`.
3. Liquidator immediately calls `liquidate()`:
   - For D3 withdraw, accrued fees are added to stored fees (`liquidateModule/main.sol:383-385`) and can be seized if liquidation proceeds to fee withdrawal (`main.sol:481-501`).
   - For D4 withdraw, accrued fees are added to stored fees (`main.sol:563-579`) and then withdrawn via `_useFeeStoredForLiquidation` (`main.sol:581-613`).
4. Liquidator recovers part of the manipulation costs via seized victim fees, increasing net profitability and worsening borrower outcome.

### Impact

The liquidated borrowers suffer an approximate loss of up to the configured `maxLiquidationPenalty` portion of the repaid debt value per liquidation in excess collateral seized relative to liquidation at an unmanipulated pool price. The liquidator gains this additional seized collateral value (net of swap fees/slippage required to manipulate and unwind the pool price), and can further amplify extraction by recycling swap-generated fees that accrue to the victim position and are then seized during the same liquidation transaction.

Add the following subsection under your existing `## Impact` section (right after the current impact paragraph). It keeps all existing content intact and demonstrates a concrete path to exceeding $10 loss.

**Loss threshold demonstration**

In `liquidateModule/main.sol`, liquidation starts with `v_.withdrawValue = v_.paybackValue` (`main.sol:245`) and then scales `withdrawValue` up by the (spot-derived) liquidation penalty factor (`main.sol:421`):

```solidity
withdrawValue ≈ paybackValue * (1000 + averageLiquidationPenalty) / 1000
```

Therefore, if MEV manipulation changes the computed `averageLiquidationPenalty` by `Δp` (where penalties use `THREE_DECIMALS = 1000` precision), the incremental over-seizure relative to an unmanipulated pool state is:

```solidity
extraSeized ≈ paybackValue * Δp / 1000
```

Concrete example (showing `extraSeized > $10` from penalty skew alone):

- Assume the effective liquidation penalties used by the liquidation logic differ across the two tokens, e.g.:
  - token0 liquidation penalty = 50 (5%)
  - token1 liquidation penalty = 150 (15%)
- Without manipulation, suppose the D3 position is roughly balanced by value at the current pool price, so:
  - `averageLiquidationPenalty ≈ (50 + 150) / 2 = 100` (10%)
- With manipulation, the liquidator pushes the pool price toward the end of the range where the position is mostly the higher-penalty token (token1), so:
  - `averageLiquidationPenalty ≈ 150` (15%)
- This yields `Δp ≈ 50` (5%).

If the liquidation repays only `paybackValue = $250` of debt, the incremental collateral seized due to the manipulated penalty becomes:

```solidity
extraSeized ≈ 250 * 50 / 1000 = $12.5
```

This exceeds the $10 threshold in a single liquidation. Even if the penalty skew is smaller (e.g., `Δp = 10` = 1%), any liquidation with `paybackValue ≥ $1,000` yields `extraSeized ≥ $10`.

### PoC

_No response_

### Mitigation

_No response_

# Issue M-3: Liquidation reverts when repaying the final remaining debt due to HF being set to type(uint256).max and compared against hfLimitForLiquidation 

Source: https://github.com/sherlock-audit/2026-01-fluid-dex-v2-judging/issues/1183 

## Found by 
Audinarey, LeoGold, Pelz, Silvermist, fuzious, iamephraim, maigadoh, p1ramide, xiaoming90

### Summary

Defining the health factor as `type(uint256).max` when `debtValue == 0` will cause a liquidation denial-of-service and prevent full debt clearance for the protocol and its liquidity providers as a liquidator will repay the last remaining debt (making `debtValue == 0`) and the liquidation will always revert on the post-liquidation `hf > hfLimitForLiquidation` check.

### Root Cause

- In `contracts/contracts/protocols/moneyMarket/core/other/helpers.sol:1051-1055` the `_getHfInfo()` helper sets `hfInfo_.hf = type(uint256).max` whenever `hfInfo_.debtValue == 0`.
- In `contracts/contracts/protocols/moneyMarket/core/liquidateModule/main.sol:622-627` the `liquidate()` flow unconditionally reverts if `_getHfInfo(...).hf > hfLimitForLiquidation`.

### Internal Pre-conditions

-

### External Pre-conditions

-

### Attack Path

`FluidMoneyMarketLiquidateModule.liquidate()` performs a liquidation (pay back debt + seize collateral), and then enforces a post-condition that the resulting health factor (HF) must not exceed the configured `hfLimitForLiquidation`:

- `liquidate()` loads `hfLimit_` from `_moneyMarketVariables` and checks:
  - `if (_getHfInfo(params_.nftId, IS_LIQUIDATE).hf > hfLimit_) revert ...HfLimitExceeded;` (`liquidateModule/main.sol:622-627`).

Separately, HF is computed in `_getHfInfo()` as:

- If `debtValue == 0`, set `hf = type(uint256).max`.
- Else, set `hf = normalizedCollateralValue * 1e18 / debtValue`.
  - (`other/helpers.sol:1051-1055`)

This combination creates a hard failure mode:

- Any liquidation that repays the final remaining debt (so total `debtValue` becomes `0`) will make `_getHfInfo()` return `hf = type(uint256).max`.
- Since `hfLimitForLiquidation` is a finite value, `type(uint256).max > hfLimitForLiquidation` will always be true.
- Therefore, the liquidation always reverts at the end, undoing the debt repayment and collateral transfer.

This is not limited to a specific position type: it applies whenever the liquidation action results in zero total debt for the NFT (i.e., the last remaining debt position is fully repaid), regardless of whether the payback/withdraw positions are NORMAL or D3/D4.

Practical consequences (all stemming from the same root cause):

1. Full liquidations are impossible
   Even if a liquidatable account has sufficient collateral to cover all debt (including liquidation penalty), liquidators cannot fully repay the account’s last remaining debt. The transaction will always revert at the final HF limit check.
2. Some unhealthy positions can become practically unliquidatable
   Liquidations enforce a minimum payback value (`v_.paybackValue >= 1e16`, i.e., $0.01) (`liquidateModule/main.sol:235-236`). For positions whose remaining debt is small enough that any valid liquidation necessarily clears all remaining debt (e.g., because paying less violates the minimum payback value or because any non-max payback amount would exceed the remaining borrow and revert in storage updates), liquidation becomes impossible: the only viable liquidation attempt is “repay all”, and “repay all” always reverts due to `hf = type(uint256).max`.
3. Residual debt must be repaid by the borrower, not enforceable by liquidators
   Liquidation is the mechanism meant to handle uncooperative borrowers. This bug forces liquidators to leave a non-zero remainder (or revert), meaning the protocol cannot rely on liquidation to fully settle positions even when it should be able to.
4. Increased exposure to future insolvency and bad debt
   When a position could have been fully closed via liquidation but cannot be, the protocol stays exposed to ongoing interest accrual and collateral price movement on the remaining debt. A position that would have been fully resolved can later become undercollateralized, turning the remaining debt into bad debt that impacts liquidity providers.

https://github.com/sherlock-audit/2026-01-fluid-dex-v2/blob/main/fluid-contracts/contracts/protocols/moneyMarket/core/operateModule/main.sol#L1

## Attack Path

### Attack path 1: Any liquidation that clears all remaining debt reverts at the end

1. A liquidator calls `liquidate()` on an NFT that is liquidatable (`hf < 1e18` at function entry) and targets the last remaining debt position as `paybackPositionIndex`.
2. The liquidator specifies “repay all” for that debt position (e.g., using `type(uint256).max` where supported), so the payback deletes the final debt amount from storage.
3. After payback and collateral withdrawal steps, the NFT now has `debtValue == 0`.
4. `liquidate()` evaluates the post-liquidation constraint:
   - `_getHfInfo(...).hf` returns `type(uint256).max` because `debtValue == 0` (`helpers.sol:1051-1055`).
   - `type(uint256).max` exceeds any finite `hfLimitForLiquidation`, so `liquidate()` reverts with `LiquidateModule__HfLimitExceeded` (`liquidateModule/main.sol:622-627`).
5. The entire liquidation (including repayment and collateral transfer) is reverted.

### Attack path 2: “Only-full-payback” unhealthy positions become unliquidatable (liquidation DoS)

1. A borrower ends up with an unhealthy NFT (HF < 1) whose remaining debt is concentrated in a single final debt position and is small enough that partial liquidation is constrained (e.g., by the minimum liquidation payback value check `v_.paybackValue >= 1e16` in `liquidateModule/main.sol:235-236`, and/or by “payback exceeds borrow” checks during payback storage updates).
2. Liquidators cannot choose a valid partial payback that both passes validation and leaves `debtValue > 0`, so the only viable attempt is to repay the full remaining debt.
3. Repaying the full remaining debt makes `debtValue == 0`, which makes HF become `type(uint256).max`.
4. The liquidation reverts on the post-liquidation HF limit check, making the position practically unliquidatable by third parties.

### Attack path 3: Forced residual debt keeps risk alive and can later crystallize into losses

1. Liquidators can partially liquidate a position but cannot clear the final remaining debt due to attack path 1 (full clearance always reverts).
2. If the borrower does not (or cannot) voluntarily repay the residual debt, the protocol is forced to carry that open debt indefinitely.
3. Over time, the residual debt accrues interest and remains exposed to collateral price changes, which can turn previously coverable debt into undercollateralized bad debt that the protocol could have avoided by allowing a final “closeout” liquidation.

### Impact

The protocol and its liquidity providers cannot fully liquidate and close liquidatable positions, because any liquidation that would repay the last remaining debt always reverts. In the worst case, this creates permanently unresolvable unhealthy positions (liquidation DoS) and/or leaves outstanding debt that cannot be forcibly repaid by liquidators, causing the protocol to accumulate bad debt and exposing liquidity providers to losses up to the full remaining debt value on affected positions, while also breaking liquidation as a core safety mechanism.

### PoC

_No response_

### Mitigation

_No response_

