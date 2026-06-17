# P82 — Source-grounded bug chain: Vultisig H-01 (ILOPool.claim shared-position fee siphon)

All line references are the audited source (`code-423n4/2024-06-vultisig` @ `befb1b1170`,
`lib/decent-bridge` n/a; ILO contracts under `src/`). Derived from source + executable behavior, **not** the answer-key text.

## Contracts / functions involved
- `src/ILOPool.sol` — `claim()` (L184-261), `buy()` (L126-176), `launch()` (L269-335), `_deductFees()` (L438-445).
- `src/base/LiquidityManagement.sol` — `addLiquidity()` / `uniswapV3MintCallback` (the single Uniswap V3 position mint).
- `src/ILOManager.sol` — `FEE_TAKER()` (the protocol fee recipient), `project().platformFee/performanceFee`.
- Uniswap V3 pool (`IUniswapV3Pool.burn/collect/positions`).

## Relevant state
- The ILOPool wraps **ONE** Uniswap V3 position: a single `(owner=ILOPool, TICK_LOWER, TICK_UPPER)` range. Every
  investor/project NFT (`_positions[tokenId]`) is an *internal accounting share* of that **one shared** Uniswap position.
- `_positions[tokenId].liquidity`, `.feeGrowthInside0/1LastX128` — per-NFT checkpoints (default **0**; never set in
  `buy()` or `launch()`).
- `FEE_TAKER` — protocol address (owner-set in ILOManager).

## Where the shared position is created/used
- `launch()` (L296-303) calls `addLiquidity(...)` once → mints the single Uniswap position with the whole ILO liquidity.
- `claim()` (L205) `pool.burn(TICK_LOWER, TICK_UPPER, liquidity2Claim)` and (L242-248)
  `pool.collect(address(this), TICK_LOWER, TICK_UPPER, type(uint128).max, type(uint128).max)` operate on that **same
  shared** position for every claimant.

## Fee accounting flow (the defect)
1. A claimant calls `claim(tokenId)`. `pool.burn(liquidity2Claim)` — in Uniswap V3, `burn` runs `_updatePosition`
   which credits **all** accrued swap fees for the position's *entire current liquidity* (i.e. every LP's share) into
   the position's `tokensOwed0/1`.
2. `pool.collect(..., type(uint128).max, type(uint128).max)` (L242) then pulls **the whole** owed balance — the
   claimant's burned principal **plus all LPs' accrued fees** — into the ILOPool contract (`amountCollected0/1`).
3. The contract computes only the **claimant's** share: `amount0/amount1` = their post-platform-fee principal + their
   own pro-rata fees (L214-231, using their NFT's `feeGrowthInside…Last` checkpoint), and pays it to the claimant
   (L252-253).
4. The **residual** `amountCollected0 - amount0` / `amountCollected1 - amount1` — which contains the **other LPs'
   accrued fees** — is sent to **`feeTaker`** (L259-260).

So the first claim sweeps every other LP's accrued fees out of the pool and hands them to `feeTaker`.

## Why a non-claimant loses / cannot claim
- Other NFTs' `feeGrowthInside…Last` checkpoints are **never updated** by an earlier claim, so each later claimant
  still *computes* its full historical fee entitlement (L214-231).
- But those fee tokens were already collected and sent to `feeTaker` in step 4; a later `burn` credits ~0 additional
  fees (feeGrowthInside unchanged absent new swaps), so `collect` returns only that claimant's principal.
- The later claim then needs `amount0 = principal_net + fees` but the contract only holds `principal`. Two outcomes by
  magnitude:
  - **fees ≤ 0.1% platform-fee buffer:** silently covered (loss masked) — observed at low swap volume.
  - **fees > buffer:** `safeTransfer` to the claimant (or the `amountCollected-amount` subtraction → `safeTransfer` to
    feeTaker) **reverts** → the claimant is **permanently unable to claim** their vested position. (Executable below.)

## Attacker / user sequence (no privileged setup)
1. Two (or more) investors `buy()` into an ILO; project `launch()` deploys the single shared position.
2. Normal trading accrues swap fees on the pool.
3. Investor A `claim()`s first (ordinary action) → A's claim routes B's accrued fees to `feeTaker`.
4. Investor B `claim()`s → reverts once accrued fees exceed the platform-fee buffer; B cannot withdraw their vested
   position. (No malicious actor required — *any* claim ordering harms whoever claims later; an attacker can also
   front-run to guarantee being first.)

## Concrete impact
LPs other than the first claimant lose their share of Uniswap fees (diverted to `feeTaker`) and, once fees are
material, **cannot claim their vested liquidity at all** (claim reverts) — funds locked. Matches the awarded **H-01**
("most users won't be able to claim their share of Uniswap fees"; judge: consequent claims fail permanently). Executable
proof shows INVESTOR_2 receiving 15,151 USDC when claiming first vs **0 (revert)** when claiming after INVESTOR.
