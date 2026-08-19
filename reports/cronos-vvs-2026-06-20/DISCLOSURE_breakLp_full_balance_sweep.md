> ⚠ DRAFT — review, edit into your own words, and submit via HackenProof (the Cronos program channel).
> Per the program rules ("No vulnerability disclosure… outside of the program without express consent"),
> do NOT send this directly to the team or post it publicly — route it through HackenProof.
> This is a LATENT issue: it is NOT exploitable on the current deployment (see "Current reachability").
> Submitting it is good-faith hardening, not a claim for a Critical reward under the current state.

# VVS ConditionalLiquidity — `breakLp` transfers the contract's entire token balance to one user (latent cross-user VVS-reward drain)

**Target:** VVS `ConditionalLiquidity` — `0xb79dcd181bc79d1774df65658fcbe9916beda3a5` (Cronos EVM, Solidity 0.6.12)
**Category (HackenProof VRT):** Smart Contract › Business Logic Errors (cross-user fund accounting)
**Severity:** Latent High/Critical (real loss-of-user-funds bug; **currently unreachable** — see below)
**Status:** No exploit performed. Findings derived from the verified source + read-only `eth_call` state reads only.

## Summary
`ConditionalLiquidity.breakLp(...)` redeems a user's LP "limit order" and, via the internal helper
`_transferTokensToUser(...)`, transfers the contract's **entire balance** of the pair's `token0` and `token1`
to the position owner — not just the amount produced by that break's `removeLiquidity` call. Because the
contract holds a **shared, persistent VVS balance** (the accumulated, still-unclaimed MasterChef rewards of
**all** users across **all** pools), breaking a position on any **VVS‑paired** LP (e.g. VVS‑WCRO, VVS‑USDC)
hands the breaking user that entire VVS balance — i.e. every other user's accrued, claimable rewards. This
drains other users' funds and leaves the contract insolvent for their subsequent claims.

## Root cause
Two facts combine:

1. **The contract holds other users' VVS.** `ConditionalLiquidity` stakes all user LP into `Craftsman`
   (MasterChef) as a single aggregated position. On every interaction `Craftsman` pays the contract the
   *whole position's* pending VVS, but the contract forwards only the **acting** user's slice (tracked via the
   `accVVSPerLp` / `rewardDebt` accumulator) and keeps the rest in its own balance for others to claim later.
   So at any time the contract's VVS balance ≈ the sum of all users' unclaimed rewards.

2. **`breakLp` sweeps the full balance, not the increment.** In `breakLp`, after `router.removeLiquidity(...)`
   sends `token0`/`token1` to the contract, the guards check the **total** contract balance, not the amount
   just produced:

   ```solidity
   require(IERC20(token0).balanceOf(address(this)) >= minToken0Amt, "... token0 below minToken0Amt");
   require(IERC20(token1).balanceOf(address(this)) >= minToken1Amt, "... token1 below minToken0Amt");
   ...
   _transferTokensToUser(_user, IERC20(token0), IERC20(token1), minToken0Amt, minToken1Amt);
   ```

   and `_transferTokensToUser` transfers the **whole** balance:

   ```solidity
   uint256 token0Bal = _token0.balanceOf(address(this));
   uint256 token1Bal = _token1.balanceOf(address(this));
   _token0.safeTransfer(_user, token0Bal);   // entire balance, incl. other users' VVS
   _token1.safeTransfer(_user, token1Bal);
   // only asserts the per-user *increase* >= minToken{0,1}Amt (passes trivially)
   ```

   When `token0` or `token1` **is VVS** (the reward token the contract custodies for everyone), the breaking
   user receives the contract's entire VVS balance.

## Attack scenario (when live)
1. A VVS‑paired pool is configured in `ConditionalLiquidity` (today VVS‑WCRO is wired as `lpPoolInfo` pid 4)
   and other users have deposited LP and accrued VVS rewards (so the contract holds VVS).
2. The attacker deposits a small amount of the same VVS‑paired LP and sets a rule (`addRule`).
3. `breakLp(pool, attacker)` is executed (the beneficiary is the position owner; with the keeper whitelist
   enabled, a keeper's normal break of the attacker's satisfied rule suffices; if the whitelist is ever
   disabled, the attacker calls it directly).
4. `removeLiquidity` adds the attacker's small VVS+WCRO to the contract; `_transferTokensToUser` then sends the
   **entire** VVS balance (the attacker's tiny share **plus all other users' unclaimed rewards**) to the
   attacker. Other users can no longer claim — the contract is insolvent for their rewards.

This is cross-user theft of already-accrued, on-demand-claimable user funds (not mere reward dilution).

## Current reachability (why this is LATENT, not currently exploitable)
Read-only Cronos state @ block ~78,324,615 (2026-06-20):
- `vvs.balanceOf(ConditionalLiquidity)` = **0** (no unclaimed rewards held)
- `accVVSPerLp` (VVS‑WCRO pid 4 and CRO‑USDC pid 3) = **0**
- `Craftsman.userInfo(pid, ConditionalLiquidity)` staked = **0**; raw LP held = **0**; `pendingVVS` = **0**
- `breakLpWhitelistEnabled()` = `true`

The contract is effectively **unused (zero TVL)**, so there are currently no other-user funds to steal. The
bug becomes a live, permissionless cross-user drain as soon as the contract is used (LP deposited into a
VVS‑paired pool so it accrues/holds VVS). We are reporting it now so it can be fixed before that happens.

## Recommended fix
Account only for the LP just redeemed, and never sweep the full contract balance:
- Snapshot `token0`/`token1` balances **before** and **after** this break's `removeLiquidity` call, and transfer
  only the **delta** (the amount this break produced) to the user.
- Never transfer the reward token (VVS) as part of a break; keep reward custody strictly separate from
  redeemed LP underlying.
- Make the `minToken{0,1}Amt` guards check the **increment**, not `balanceOf(address(this))`.

## Notes
- No transaction was sent to mainnet or any public testnet; this is based on the verified source and read-only
  `eth_call`s. No PoC is included because the live contract holds no funds to demonstrate against; a fork PoC
  can be provided on request that seeds two users into a VVS‑paired pool and shows the second user's break
  draining the first user's accrued VVS.
