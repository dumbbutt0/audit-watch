# P120 — Source trace: FeeCollector.collectProtocolFees (ramses-2024-10)

Subject: `contracts/CL/gauge/FeeCollector.sol`. Read-only; cited for framing only — runtime decides.

## The function (permissionless, arbitrary pool)
`function collectProtocolFees(IRamsesV3Pool pool) external override` — **no access modifier** → permissionless;
`pool` is an **arbitrary caller-supplied address**.

1. `token0 = pool.token0(); token1 = pool.token1();`
2. Gauge resolution via the **trusted `voter`**:
   - `gauge = voter.gaugeForPool(pool); isAlive = voter.isAlive(gauge);`
   - if `gauge == 0 || !isAlive`: `toPool = voter.poolRedirect(pool); gauge = voter.gaugeForPool(toPool); isAlive = voter.isAlive(gauge);`
3. **No-gauge branch** — `if (gauge == 0 || !isAlive || !isTokenLive)`:
   `pool.collectProtocol(treasury, type(uint128).max, type(uint128).max);` → **all protocol fees go straight to `treasury`**, then `return`.
4. **Gauge branch**:
   - `feeDist = IFeeDistributor(voter.feeDistributorForGauge(gauge));`
   - `pool.collectProtocol(address(this), max, max);` → fees pulled into the FeeCollector.
   - `amount0 = token0.balanceOf(address(this)); amount1 = token1.balanceOf(address(this));`  ← **entire balance, not the collection delta**.
   - treasury split: `amountTreasury = amount * treasuryFees / BASIS; amount -= amountTreasury;` then
     `token.safeTransfer(treasury, amountTreasury)` (only if `> 0`).
   - `token.approve(feeDist, amount); feeDist.notifyRewardAmount(token, amount);` (only if `> 0`).

## Recipients — none is caller-controlled
- `treasury` — storage var, set only via `onlyTreasury` (`setTreasury`).
- `address(this)` — the FeeCollector itself.
- `feeDist` — `voter.feeDistributorForGauge(voter.gaugeForPool(pool))`, i.e. resolved through the **trusted voter**.

The caller (`msg.sender`) is never a transfer recipient and never an argument to a transfer/notify. The only
caller-influence is *which* `pool` is passed.

## State / access (for the harness setup)
- `treasury` (address), `treasuryFees` (uint256, ≤ BASIS=10_000), `voter` (IVoter), `isTokenLive` (bool).
- `constructor` calls `_disableInitializers()` (OZ `Initializable`) → the implementation must run **behind a proxy**;
  `initialize(_treasury, _voter)` is the `initializer`.
- Setters `setTreasury` / `setTreasuryFees` / `setIsLive` are all `onlyTreasury` (`require(msg.sender == treasury, …)`).

## Structural quirk (probe target)
Step 4 uses `token.balanceOf(address(this))` for the notify amount. Any residual the FeeCollector holds (a prior
dust/donation) is swept into **the currently-collected pool's** fee distributor — a cross-pool *misattribution*.
But producing a residual requires a **donation** (someone sends tokens to the FeeCollector, a self-loss); the caller
gains nothing. Framed as a runtime question, not a source conclusion.

## Framed runtime question (→ harness)
`collectProtocolFees` is a permissionless trigger over an arbitrary `pool` with fully hardcoded/voter-resolved
recipients. Can a permissionless caller **redirect or extract** protocol fees to an address they control, or break
fee accounting via the `balanceOf(this)` notify amount? → answered by the harness (runtime), not this trace.
